#!/usr/bin/env python3
"""Read-only Spark telemetry; long-form CSV, blank value plus error on failed reads."""

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
import time


def sensor_files(base):
    for zone in sorted((base / 'thermal').glob('thermal_zone*')):
        label = zone.name
        try:
            label = (zone / 'device/path').read_text().strip()
        except OSError:
            pass
        yield 'thermal', zone.name, label, zone / 'temp', 1000, 'C'
    for hw in sorted((base / 'hwmon').glob('hwmon*')):
        try:
            name = (hw / 'name').read_text().strip()
        except OSError:
            continue
        if name not in ('nvme', 'acpi_fan', 'dgx_ec_fan'):
            continue
        for pattern, scale, unit in [('temp*_input', 1000, 'C'), ('fan*_input', 1, 'RPM')]:
            for path in sorted(hw.glob(pattern)):
                label = path.stem
                try:
                    label = path.with_name(path.name.replace('_input', '_label')).read_text().strip()
                except OSError:
                    pass
                yield name, hw.name, label, path, scale, unit


def rows(base=Path('/sys/class')):
    found = False
    for source, device, label, path, scale, unit in sensor_files(base):
        found = True
        try:
            yield source, device, label, int(path.read_text().strip()) / scale, unit, ''
        except (OSError, ValueError) as exc:
            yield source, device, label, '', unit, str(exc)
    if not found:
        yield 'sysfs', '', '', '', '', 'No matching thermal/fan/NVMe sensors found'
    try:
        yield 'rtc', 'rtc0', 'time', (base / 'rtc/rtc0/time').read_text().strip(), 'UTC', ''
    except OSError as exc:
        yield 'rtc', 'rtc0', 'time', '', 'UTC', str(exc)
    fields = ['temperature.gpu', 'clocks.gr', 'power.draw', 'utilization.gpu', 'clocks_event_reasons.active']
    units = ['C', 'MHz', 'W', '%', 'bitmask']
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=' + ','.join(fields),
                                 '--format=csv,noheader,nounits'], check=True,
                                capture_output=True, text=True, timeout=10)
        if not result.stdout.strip():
            raise ValueError('nvidia-smi returned no GPU rows')
        for index, values in enumerate(csv.reader(result.stdout.splitlines())):
            if len(values) != len(fields):
                raise ValueError('Unexpected nvidia-smi CSV column count')
            for label, value, unit in zip(fields, values, units):
                value = value.strip()
                missing = not value or 'N/A' in value or 'Not Supported' in value
                yield 'gpu', str(index), label, '' if missing else value, unit, 'unavailable' if missing else ''
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        yield 'gpu', '', '', '', '', str(exc)


def positive(value):
    parsed = float(value)
    if not 0 < parsed < float('inf'):
        raise argparse.ArgumentTypeError('must be finite and positive')
    return parsed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--duration', type=positive, default=900)
    parser.add_argument('--interval', type=positive, default=2)
    args = parser.parse_args()
    writer = csv.writer(sys.stdout)
    writer.writerow(['timestamp_utc', 'source', 'device', 'sensor', 'value', 'unit', 'error'])
    deadline = time.monotonic() + args.duration
    failed = False
    try:
        while time.monotonic() < deadline:
            stamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds')
            for row in rows():
                writer.writerow([stamp, *row])
                failed |= bool(row[-1])
            sys.stdout.flush()
            remaining = deadline - time.monotonic()
            if remaining > 0:
                time.sleep(min(args.interval, remaining))
    except KeyboardInterrupt:
        return 130
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
