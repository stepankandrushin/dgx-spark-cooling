import importlib.machinery
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch, Mock, call


ROOT = Path(__file__).resolve().parents[1]


def load(name, filename):
    loader = importlib.machinery.SourceFileLoader(name, str(ROOT / 'scripts' / filename))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


fan = load('spark_fan', 'spark-fan')
sampler = load('thermal_sample', 'thermal-sample.py')


class FanGuardTests(unittest.TestCase):
    def test_unsupported_firmware_never_loads_or_writes(self):
        with tempfile.TemporaryDirectory() as td, \
                patch.object(fan.os, 'geteuid', return_value=0), \
                patch.object(fan, 'check_identity'), \
                patch.object(fan, 'ec_version', return_value=0x03000d07), \
                patch('builtins.open', return_value=open(Path(td) / 'lock', 'w')), \
                patch.object(fan.subprocess, 'run') as process, \
                patch.object(fan, 'write_state') as write:
            with self.assertRaisesRegex(RuntimeError, 'EC 3.5.8'):
                fan.change(8)
            process.assert_not_called()
            write.assert_not_called()

    def run_change(self, **overrides):
        defaults = {'check_identity': Mock(), 'ec_version': Mock(return_value=fan.EC_VERSION),
                    'check_ec_link': Mock(), 'temperatures': Mock(return_value=[('CPU', 50)]),
                    'cooling_device': Mock(return_value=Path('/fake/device')),
                    'fan_readings': Mock(return_value=[('a', 4000), ('b', 5000)]),
                    'driver_fan_readings': Mock(return_value=[4000, 5000]),
                    'status': Mock(return_value=True), 'write_state': Mock()}
        defaults.update(overrides)
        with tempfile.TemporaryDirectory() as td, \
                patch.object(fan.os, 'geteuid', return_value=0), \
                patch('builtins.open', return_value=open(Path(td) / 'lock', 'w')), \
                patch.multiple(fan, **defaults), patch.object(fan.time, 'sleep'), \
                patch.object(fan.subprocess, 'run') as process:
            try:
                fan.change(8)
            finally:
                process.assert_not_called()
        return defaults

    def test_frozen_ec_never_writes(self):
        write = Mock()
        with self.assertRaisesRegex(RuntimeError, 'frozen'):
            self.run_change(check_ec_link=Mock(side_effect=RuntimeError('frozen')), write_state=write)
        write.assert_not_called()

    def test_partial_fan_stop_refused(self):
        write = Mock()
        with self.assertRaisesRegex(RuntimeError, 'Stopped-fan'):
            self.run_change(fan_readings=Mock(return_value=[('a', 0), ('b', 5000)]), write_state=write)
        write.assert_not_called()

    def test_failed_post_check_attempts_auto(self):
        write = Mock()
        with self.assertRaisesRegex(RuntimeError, 'Cooling check failed'):
            self.run_change(status=Mock(side_effect=[True, False]), write_state=write)
        self.assertEqual(write.call_args_list, [call(Path('/fake/device'), 8), call(Path('/fake/device'), 0)])

    def test_missing_registered_identity_refused(self):
        with patch.object(fan, 'IDENTITY', Path('/nonexistent/identity.json')):
            with self.assertRaises(OSError):
                fan.check_identity()

    def test_mismatched_identity_refused(self):
        fake = Mock()
        fake.lstat.return_value = Mock(st_mode=0o100600, st_uid=0)
        fake.read_text.return_value = json.dumps({'hostname': 'some-other-spark', 'serial': 'example'})
        with patch.object(fan, 'IDENTITY', fake), patch.object(fan, 'read', return_value='example'):
            with self.assertRaisesRegex(RuntimeError, 'Hostname/serial'):
                fan.check_identity()

    def test_identity_must_not_be_writable_by_others(self):
        fake = Mock()
        fake.lstat.return_value = Mock(st_mode=0o100666, st_uid=0)
        with patch.object(fan, 'IDENTITY', fake):
            with self.assertRaisesRegex(RuntimeError, 'root-owned'):
                fan.check_identity()

    def test_identity_symlink_refused(self):
        fake = Mock()
        fake.lstat.return_value = Mock(st_mode=0o120777, st_uid=0)
        with patch.object(fan, 'IDENTITY', fake):
            with self.assertRaisesRegex(RuntimeError, 'root-owned'):
                fan.check_identity()

    def test_readback_mismatch_is_failure(self):
        with tempfile.TemporaryDirectory() as td, patch.object(fan, 'current_state', return_value=0):
            with self.assertRaisesRegex(RuntimeError, 'readback mismatch'):
                fan.write_state(Path(td), 8)

    def test_wrong_cooling_device_is_never_selected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'cooling_device0'
            path.mkdir(); (path / 'type').write_text('Fan')
            with patch.object(fan, 'THERMAL', Path(td)):
                self.assertIsNone(fan.cooling_device())


class SamplerTests(unittest.TestCase):
    def test_multiple_drives_and_read_error_are_explicit(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            for index, value in enumerate(('43000', '47000', 'broken')):
                hw = base / 'hwmon' / f'hwmon{index}'
                hw.mkdir(parents=True); (hw / 'name').write_text('nvme')
                (hw / 'temp1_input').write_text(value)
            with patch.object(sampler.subprocess, 'run', side_effect=FileNotFoundError('nvidia-smi')):
                rows = list(sampler.rows(base))
            nvme = [r for r in rows if r[0] == 'nvme']
            self.assertEqual([r[3] for r in nvme], [43, 47, ''])
            self.assertTrue(nvme[2][-1])
            self.assertTrue(any(r[0] == 'gpu' and r[-1] for r in rows))

    def test_unavailable_gpu_values_are_not_zero(self):
        result = subprocess.CompletedProcess([], 0, stdout='50, 2190, N/A, 99, 0x0\n')
        with tempfile.TemporaryDirectory() as td, patch.object(sampler.subprocess, 'run', return_value=result):
            rows = list(sampler.rows(Path(td)))
        power = next(r for r in rows if r[2] == 'power.draw')
        self.assertEqual(power[3], '')
        self.assertEqual(power[-1], 'unavailable')


if __name__ == '__main__':
    unittest.main()
