# Hold a 9,000 RPM minimum fan speed

The fan floor gives a substantial measured temperature reduction in our sustained
decode test. It is also the most involved method: the pinned driver needs EC
3.5.8, whose idle fan-stop defect needs a workaround. Read the whole procedure
before changing firmware. If you prefer current stock firmware, use placement
and the clock cap and keep the stock fan controller.

## What the numbers mean

`spark-fan set 66` requests the next supported floor above 66% of 13,500 RPM:
9,000 RPM. This is a **minimum**, not PWM duty or a fixed equal speed. The firmware
can request more cooling. Fan 1 saturates at 9,000 RPM; fan 2 at 13,500 RPM.
`spark-fan auto` removes the added floor through the driver's authenticated unset
value, `0xffff`. It does not command stopped fans.

With the 2,200 MHz GPU cap already active, the four-machine mean GPU temperature
fell from 60.0 to 52.7 °C, and NVMe from 48.6 to 42.9 °C. Increasing the floor to
13,500 gave only another 1.5 °C GPU and 0.9 °C NVMe reduction. We chose 9,000 for
cooler storage, accepting noise. Storage lifespan and sound-pressure levels were
not measured. See [the complete sweep](results.md).

## 1. Establish compatibility and recovery access

The validated combination is NVIDIA DGX Spark, EC 3.5.8 (`0x03000508`), SoC
2.158.15, signed driver 0.1.4 at commit
`d121e06f0b62837632656ba95dc0d6445951142c`, kernel 7.0.0-1025-nvidia.
Keep the SoC and USB-C PD firmware unchanged during this procedure.

```sh
uname -r
sudo fwupdmgr get-devices
mokutil --sb-state
sudo dmidecode -t 45
python3 scripts/spark-fan status
```

Record the installed EC version, its fwupd device ID and the current kernel.
EC 3.13.7 is incompatible with this driver's control interface. Do not patch out
its capability checks. A different kernel needs a successful build and validation;
it is outside the exact tested pairing above.

Stop inference jobs before firmware work. Have the machine's preboot console
available for MOK enrollment, and a person able to disconnect and reconnect that
individual machine's power. Warm reboots can leave the EC link frozen, including
on newer firmware. Do not plan this as an unattended remote firmware installation.

## 2. Install the idle-fan workaround before using the older EC

On EC 3.5.8, an uncabled ConnectX-7 can power down and leave both fans stopped.
Blocking its hotplug module prevents that power-down. Install from this repo:

```sh
sudo install -m 0644 scripts/no-cx7-hotplug.conf /etc/modprobe.d/no-cx7-hotplug.conf
sudo update-initramfs -u -k "$(uname -r)"
```

This takes effect after reboot. Keep it even with a permanent floor: if the floor
service fails, the machine can return to automatic control. It also protects a
connected machine if its QSFP cable is removed later.

The workaround keeps extra hardware powered. Approximately 17 W is an upstream
report for an otherwise uncabled adapter, not a measurement from our machines.
That is not an additional 17 W relative to a connected adapter already powered on.
See the [NVIDIA discussion](https://forums.developer.nvidia.com/t/dgx-spark-fans-stop-when-the-screen-goes-dark-or-running-from-ssh-box-gets-too-hot-to-touch-fire-hazard/378945/24),
posts 22 and 24.

## 3. Obtain both EC images and verify them

Skip the downgrade if the EC already reads 3.5.8. Otherwise obtain the official
signed downgrade and rollback images. These are for NVIDIA DGX Spark, not partner
GB10 products. Downloading does not install firmware:

```sh
mkdir -p firmware
cd firmware
old=3f220245f0803c4927490d01a8403560687fe6a631ec17e2c2d7359f76c3bef1
new=c3fab69bb1ef6d22e1a1d28a0bbc05319fb321bf81af4fd574349d2b0b23fa30
curl --fail --location --user-agent fwupd/2.0.20 -O "https://fwupd.org/downloads/${old}-ec_fused.cab"
curl --fail --location --user-agent fwupd/2.0.20 -O "https://fwupd.org/downloads/${new}-ec_fused.cab"
printf '%s  %s-ec_fused.cab\n' "$old" "$old" "$new" "$new" | sha256sum --check
cd ..
```

Both checks must pass. Read [capsule provenance](sources.md#firmware)
and compare the device's LVFS release metadata. Retain the 3.13.7 image for rollback.
Select the **EC device ID reported by your machine**, not the SoC or USB-C PD device:

```sh
EC_DEVICE_ID='REPLACE_WITH_YOUR_EC_DEVICE_ID'
sudo fwupdmgr local-install firmware/3f220245f0803c4927490d01a8403560687fe6a631ec17e2c2d7359f76c3bef1-ec_fused.cab "$EC_DEVICE_ID" --allow-older
sudo systemctl reboot
```

Inspect fwupd's device and version confirmation. Do not override verification
failures. After reboot, run `fwupdmgr get-devices` and require EC 3.5.8. Check that
SoC and PD versions match your recorded values.

## 4. Check EC health and genuinely idle cooling

From the repo, inspect repeated status readings for at least three minutes:

```sh
for sample in 1 2 3 4 5 6 7; do
    date -u
    python3 scripts/spark-fan status || break
    sleep 30
done
lsmod | rg mtk_pcie_hotplug
lspci -nn | rg -i 'Mellanox|ConnectX'
journalctl -b -k | rg 'rtc-efi|Cable removal'
```

Use `grep -E` instead of `rg` if ripgrep is not installed. The hotplug-module search
should find nothing; ConnectX-7 functions should remain present. The RTC must
advance with UTC, temperatures must read sensibly, and both fans must run.
There should be no EC clock error or CX7 cable-removal event.

Then leave inference stopped and validate at least ten genuinely idle minutes,
including the intended headless/uncabled condition. Keep observing both fan
readings and temperature. A short successful load test misses the idle defect.
Do not query an uncabled adapter with mstflint as part of this procedure.

If the EC clock freezes or fan readings become stale, keep workloads stopped.
Shut down cleanly, physically power-cycle only the affected machine, and repeat
the three-minute health check. A power-button press may be needed after reconnecting.
Do not repeatedly force module loading or treat stale RPM as evidence of cooling.

## 5. Build and sign the pinned driver

Follow the [upstream installation guide](https://github.com/christopherowen/dgx-spark-fan-control/blob/d121e06f0b62837632656ba95dc0d6445951142c/docs/installation.md).
The manual signed route used here is:

```sh
sudo apt-get install git build-essential linux-headers-"$(uname -r)" python3 openssl mokutil
mkdir -p "$HOME/src"
git clone https://github.com/christopherowen/dgx-spark-fan-control.git "$HOME/src/dgx-spark-fan-control"
cd "$HOME/src/dgx-spark-fan-control"
git checkout d121e06f0b62837632656ba95dc0d6445951142c
./scripts/check
./scripts/generate-signing-key
sudo mokutil --import "$HOME/.local/share/dgx-spark-fan-control/keys/MOK.der"
sudo systemctl reboot
```

If an enrolled signing pair already exists, reuse it instead of generating another.
Choose an enrollment password when prompted, then complete **Enroll MOK → Continue
→ Yes** at the preboot console. Keep the private key outside this checkout.
After reboot, recheck EC health, return to the driver checkout, then:

```sh
mokutil --test-key "$HOME/.local/share/dgx-spark-fan-control/keys/MOK.der"
./scripts/build-sign
sudo install -D -m 0644 kernel/dgx_ec_fan_control.ko "/lib/modules/$(uname -r)/updates/dgx_ec_fan_control.ko"
sudo depmod -a
modinfo -F signer dgx_ec_fan_control
sudo install -m 0755 userspace/dgx_fan_control.py /usr/local/sbin/dgx-fan-control
```

Require successful key enrollment and a signed module for the running kernel.
This route has no DKMS registration: repeat build/sign/install after a kernel
change, using the same enrolled key. Do not install upstream's boot-load entry
or curve service alongside this guide's floor service.

## 6. Register this Spark and validate manual control

Return to the **cooling repository**. Registering saves this machine's identity
locally; it is never included in the public repository. Review the target
hostname and serial locally before running this step:

```sh
sudo install -d -m 0755 /etc/dgx-spark-cooling
sudo python3 - <<'PY'
import json, socket
from pathlib import Path
path = Path('/etc/dgx-spark-cooling/identity.json')
identity = {'hostname': socket.gethostname(),
            'serial': Path('/sys/class/dmi/id/product_serial').read_text().strip()}
with path.open('x') as stream:
    json.dump(identity, stream)
path.chmod(0o600)
PY
sudo install -m 0755 scripts/spark-fan /usr/local/sbin/spark-fan
sudo spark-fan auto
dgx-fan-control status
sudo spark-fan set 50
sudo spark-fan auto
sudo spark-fan set 66
spark-fan status
```

The first auto loads the module only after identity, firmware, RTC, fan telemetry
and temperature checks. Require upstream status `state=0/12` after auto and a
`dgx_ec_fan_floor` cooling device. `set 50` requests 7,200 RPM; `set 66` requests
9,000. Each operation checks readback and prints before/after telemetry. Real RPM
can settle a little below the requested floor. If a check fails, investigate
before continuing. Restoring automatic can itself fail if EC communication fails.

## 7. Measure cooldown, then keep the floor across boot

With the clock cap fixed and the same workload running, record an automatic
baseline, then each floor for at least ten minutes. Analyse the last four minutes
of each interval; extend it if storage has not settled. Return to automatic as
a final control. See [the measurement recipe](results.md#repeat-the-experiment).

After choosing the floor, install from the cooling repo:

```sh
sudo install -m 0644 systemd/spark-fan-floor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now spark-fan-floor.service
systemctl status spark-fan-floor.service --no-pager
spark-fan status
```

Stop workloads and reboot when ready; verify the floor, EC health, idle behavior
and sustained-load temperatures again. The unit retries failures every 30 seconds
for roughly five minutes. A failed unit needs attention. Healthy firmware normally
retains automatic cooling if loading fails, but a failed EC transport cannot
guarantee restoration. The workaround is still required.

## Undo and return to newer firmware

To remove only the added floor:

```sh
sudo systemctl disable --now spark-fan-floor.service
sudo spark-fan auto
dgx-fan-control status
```

Keep the CX7 workaround while EC 3.5.8 remains installed. To leave this setup
completely, stop inference, verify automatic state, unload the module, then install
the verified rollback capsule from the cooling checkout:

```sh
sudo modprobe -r dgx_ec_fan_control
EC_DEVICE_ID='REPLACE_WITH_YOUR_EC_DEVICE_ID'
sudo fwupdmgr local-install firmware/c3fab69bb1ef6d22e1a1d28a0bbc05319fb321bf81af4fd574349d2b0b23fa30-ec_fused.cab "$EC_DEVICE_ID"
sudo systemctl reboot
```

Require EC 3.13.7 readback and a healthy RTC/fans. Only then remove the workaround,
rebuild initramfs, reboot and repeat the ten-minute idle check:

```sh
sudo rm /etc/modprobe.d/no-cx7-hotplug.conf
sudo update-initramfs -u -k "$(uname -r)"
sudo systemctl reboot
```

The disabled fan unit and unused module can remain for reference; if removing them,
remove only files installed by this guide and run `depmod -a` and
`systemctl daemon-reload`. Deleting a signing key file does not revoke its MOK
enrollment. The independent GPU cap can stay or be [undone separately](gpu-clock-cap.md#undo).

## Attempts that did not work

Stock ACPI Fan level-100 writes were accepted without increasing measured RPM.
Writing zero to those devices has no established automatic-reset meaning on
this setup. We do not use them. Increasing the floor did not demonstrate an
inference-speed improvement, and a short initial test failed to reveal the idle
fan-stop defect. Neither firmware downgrade alone nor successful `modprobe`
proves the cooling system is ready.
