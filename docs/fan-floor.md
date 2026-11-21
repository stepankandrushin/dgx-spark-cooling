# Hold a 9,000 RPM minimum fan speed

The Spark has two internal fans, and their speed is set automatically by its
embedded controller (EC). Under our sustained load it kept them at about 3,600
and 5,400 RPM. Here we use a separate open-source driver to tell the EC never to
go below 9,000 RPM, and the EC can still spin the fans faster if it wants to.

In our tests it brought temperatures down a lot, even with the clock cap already
on. But it's also by far the most work. The driver works only with the older EC
firmware 3.5.8 so you have to downgrade, and this firmware has a bug that can
stop both fans at idle, so you also need a workaround for it. Please read the
whole guide before you change any firmware. If you'd rather stay on current
firmware, then use the [clock cap](gpu-clock-cap.md) and leave the fans on
automatic. In our [enclosure test](results.md#printed-enclosure-against-the-fan-floor),
two Sparks in the printed enclosure on current firmware and automatic fans
stayed within a few degrees of two floored ones under the same load.

## What it does and what it changed for us

`spark-fan set 66` asks for the lowest supported floor at or above 66% of
13,500 RPM, and that is 9,000 RPM. This number is a minimum fan speed, not a PWM
duty, and the two fans don't run at the same fixed speed - fan 1 tops out at
9,000 RPM and fan 2 at 13,500 RPM. `spark-fan auto` removes the floor again. It
sends the driver's "no floor" value `0xffff` and never tells the fans to stop.

We ran this test with the 2,200 MHz GPU cap already on. Across four machines the
average GPU temperature fell from 60.0 to 52.7 °C, and the NVMe drives from 48.6
to 42.9 °C. Going all the way to 13,500 RPM took off only another 1.5 °C on the
GPU and 0.9 °C on the drives. We chose 9,000 RPM - for us cooler drives are
worth the noise. We didn't measure noise levels or drive lifespan. The whole
sweep is in [results](results.md#fan-floor).

## 1. Check that your Spark matches, and plan for recovery

This is the combination we ran:

- NVIDIA DGX Spark
- EC 3.5.8 `0x03000508`
- SoC 2.158.15
- the signed driver 0.1.4 at commit `d121e06f0b62837632656ba95dc0d6445951142c`
- kernel 7.0.0-1025-nvidia

Don't change the SoC or USB-C PD firmware during this procedure.

```sh
uname -r
sudo fwupdmgr get-devices
mokutil --sb-state
sudo dmidecode -t 45
python3 scripts/spark-fan status
```

Write down the EC version, the EC's fwupd device ID and the kernel. With EC
3.13.7 the driver doesn't work, and don't patch out its checks to force it. We
haven't tested other kernels, so the driver has to build and pass the checks
below before you rely on it.

First stop inference. To enroll a signing key you will need the machine's boot
console. You will also need someone who can unplug this one Spark and plug it
back in, because a warm reboot can leave the EC unresponsive, even on newer
firmware. So don't plan this as an unattended remote firmware update.

## 2. Install the idle-fan workaround before the downgrade

On EC 3.5.8 a ConnectX-7 network adapter with no cable can power down, and when
that happens, both fans can stop. If you block the adapter's hotplug module, it
stays powered, so the fans keep running. From this repository:

```sh
sudo install -m 0644 scripts/no-cx7-hotplug.conf /etc/modprobe.d/no-cx7-hotplug.conf
sudo update-initramfs -u -k "$(uname -r)"
```

It takes effect after the next reboot. Keep it even after the floor is set up,
because if the floor service ever fails, the fans fall back to automatic, and the
bug can come back. It also protects a machine whose QSFP cable is unplugged
later.

The price is extra power, since the adapter stays on. An upstream report puts it
at about 17 W for an adapter with no cable, we didn't measure that ourselves. If
your adapter is already cabled and powered, it doesn't add another 17 W. See the
[NVIDIA forum discussion](https://forums.developer.nvidia.com/t/dgx-spark-fans-stop-when-the-screen-goes-dark-or-running-from-ssh-box-gets-too-hot-to-touch-fire-hazard/378945/24),
posts 22 and 24

## 3. Download and verify both EC images

If your EC already reports 3.5.8 skip this step. If not, download NVIDIA's
signed 3.5.8 image for the downgrade and the 3.13.7 image for going back later.
Both are only for NVIDIA DGX Spark, not for partner GB10 machines. Downloading
installs nothing:

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

Both checksums must pass. See [where the images come from](sources.md#firmware)
and compare with the LVFS release information for your device. Keep the 3.13.7
image, you need it to go back. When you install, use **the EC device ID that
your machine reports**, not the SoC and not the USB-C PD device:

```sh
EC_DEVICE_ID='REPLACE_WITH_YOUR_EC_DEVICE_ID'
sudo fwupdmgr local-install firmware/3f220245f0803c4927490d01a8403560687fe6a631ec17e2c2d7359f76c3bef1-ec_fused.cab "$EC_DEVICE_ID" --allow-older
sudo systemctl reboot
```

Read what fwupd reports about the device and version. If verification fails -
stop, don't override it. After the reboot `fwupdmgr get-devices` must show EC
3.5.8 with the SoC and PD versions the same as you wrote down.

## 4. Check the EC is healthy, including at idle

From the repository, take status readings for at least three minutes:

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

If you don't have ripgrep, use `grep -E` in place of `rg` in these commands.
What you should see:

- The search for the hotplug module finds nothing, but the ConnectX-7 devices
  are still listed.
- The EC clock goes forward together with UTC.
- Temperatures look sensible and both fans are spinning.
- There are no EC clock errors and no CX7 cable-removal events.

Then leave inference off and watch it for at least ten minutes of real idle,
set up the way it will normally run - headless, and with the adapter uncabled if
that's how you use it. All this time keep watching both fan speeds and the
temperatures. A short load test won't show the idle bug. During this check don't
query an uncabled adapter with mstflint.

If the EC clock stops or the fan readings stop changing, keep workloads off.
Shut down cleanly, unplug only this Spark, plug it back in and run the
three-minute check again. After reconnecting you may have to press the power
button. Don't keep forcing the module to load, and a stuck RPM reading is not
proof that the fans are working.

## 5. Build and sign the driver

This follows the
[upstream installation guide](https://github.com/christopherowen/dgx-spark-fan-control/blob/d121e06f0b62837632656ba95dc0d6445951142c/docs/installation.md),
its manual signed build:

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

If you already have an enrolled signing key, use it, don't make a new one. When
asked, choose an enrollment password, and then at the boot console choose
**Enroll MOK → Continue → Yes**. Keep the private key outside this repository.
After the reboot check EC health again, go back to the driver checkout and run:

```sh
mokutil --test-key "$HOME/.local/share/dgx-spark-fan-control/keys/MOK.der"
./scripts/build-sign
sudo install -D -m 0644 kernel/dgx_ec_fan_control.ko "/lib/modules/$(uname -r)/updates/dgx_ec_fan_control.ko"
sudo depmod -a
modinfo -F signer dgx_ec_fan_control
sudo install -m 0755 userspace/dgx_fan_control.py /usr/local/sbin/dgx-fan-control
```

The key must be enrolled and the module signed for the kernel you're running.
This build isn't registered with DKMS, so after every kernel update you have to
build, sign and install it again with the same key. Don't install upstream's
boot-load entry or fan-curve service, otherwise they conflict with this guide's
floor service.

## 6. Register this Spark and try the floor by hand

Now go back to **this cooling repository**. The next step saves this machine's
hostname and serial number to a local file, and the wrapper won't change fan
settings on a machine that doesn't match it. The file stays on the Spark and
never goes into the repository. Before you run it, check the hostname and
serial:

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

The first `auto` loads the driver only after it has checked the machine
identity, the firmware, the EC clock, the fan readings and the temperatures.
After `auto` upstream's status must show `state=0/12` and a `dgx_ec_fan_floor`
cooling device must exist. `set 50` asks for 7,200 RPM and `set 66` for 9,000
RPM. Every command reads the setting back and prints the fan readings before and
after. The actual speed can settle a little below the requested floor. If any
check fails, first find out why, and only then go on. If the EC stops
responding, even going back to automatic can fail.

## 7. Measure the difference, then keep the floor after reboot

The clock cap and the workload stay the same. Record a run on automatic, then
each floor you want to compare, at least ten minutes each. Use the last four
minutes of each, or longer if the drives haven't settled. At the end run
automatic again as a check. The details are in the
[measurement recipe](results.md#repeat-the-experiment).

Once you've picked a floor, install the boot service from this repository:

```sh
sudo install -m 0644 systemd/spark-fan-floor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now spark-fan-floor.service
systemctl status spark-fan-floor.service --no-pager
spark-fan status
```

At a convenient time stop workloads and reboot. Then check the floor, EC health,
idle behaviour and temperatures under long load again. If the service fails, it
retries every 30 seconds for about five minutes, and if it stays failed, you
have to look into it. With healthy firmware, if the driver can't load, the fans
normally stay on automatic. But if the EC link itself has failed, nothing can
guarantee that, and this is exactly why the idle workaround stays in place.

## Undo, and go back to newer firmware

To remove only the floor:

```sh
sudo systemctl disable --now spark-fan-floor.service
sudo spark-fan auto
dgx-fan-control status
```

As long as EC 3.5.8 is installed, keep the CX7 workaround. To undo everything,
stop inference, make sure the fans are on automatic, unload the driver, and
install the verified 3.13.7 image from this repository:

```sh
sudo modprobe -r dgx_ec_fan_control
EC_DEVICE_ID='REPLACE_WITH_YOUR_EC_DEVICE_ID'
sudo fwupdmgr local-install firmware/c3fab69bb1ef6d22e1a1d28a0bbc05319fb321bf81af4fd574349d2b0b23fa30-ec_fused.cab "$EC_DEVICE_ID"
sudo systemctl reboot
```

Remove the workaround only after you've made sure the EC reports 3.13.7 and the
EC clock and fans are healthy. Then remove it, rebuild the initramfs, reboot and
do the ten-minute idle check again:

```sh
sudo rm /etc/modprobe.d/no-cx7-hotplug.conf
sudo update-initramfs -u -k "$(uname -r)"
sudo systemctl reboot
```

The disabled service and the unused driver can stay installed. If you remove
them, delete only what this guide installed, and after that run `depmod -a` and
`systemctl daemon-reload` as well. Note that deleting the signing key file
doesn't remove its MOK enrollment. The GPU cap is a separate thing, keep it or
[undo it](gpu-clock-cap.md#undo) on its own.

## What didn't work

- Writing level 100 to the Spark's standard ACPI fan devices was accepted, but
  the fans didn't speed up. We also couldn't confirm that writing zero to them
  gives automatic control back on this setup, so we don't touch them at all.
- Faster fans didn't make inference any faster.
- Our first short test missed the idle fan-stop bug, it showed up only at real
  idle.
- If the firmware downgrade or the `modprobe` succeeded, it doesn't mean the
  setup is ready. Run all the checks above.
