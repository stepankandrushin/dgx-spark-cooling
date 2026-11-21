# DGX Spark Cooling

We run LLM inference on NVIDIA DGX Sparks, and under long load they get warm.
To cool them we did four things:

1. Took off the decorative plastic cover on the bottom.
2. Put two Sparks into an ABS enclosure that I designed and printed, with 120 mm
   fans blowing air through it.
3. Capped the GPU clock at 2,200 MHz.
4. Raised the minimum speed of the Spark's own fans to 9,000 RPM.

Here you have the print files, a guide for each step, our measurements, and how
to undo every change.

![The printed two-Spark enclosure](3d-print/DGX_Spark_Duo_photo_01.jpg)

**Print files:** [body](3d-print/DGX_Spark_Duo_body.stl) ·
[cap](3d-print/DGX_Spark_Duo_cap.stl) ·
[preview](3d-print/DGX_Spark_Duo_preview.png) ·
[section drawing](3d-print/DGX_Spark_Plan.png) ·
[photos and print notes](3d-print/README.md)

## The methods we use

### 1. Remove the bottom cover

The bottom of the Spark is just a decorative plastic panel, and behind it are
the NVMe drive and the Wi-Fi antennas. With the panel off, air can move across
the drive area. It comes off by hand and goes back on the same way. But after
that the Spark has to stand on its edges with space underneath, so don't put it
flat on a table, otherwise air can't get there.

![Pulling the bottom cover off a DGX Spark by hand](docs/images/bottom-cover-off.gif)

We haven't measured this change on its own. Guide - [bottom cover](docs/bottom-cover.md).

### 2. Put two Sparks in the ABS enclosure

The enclosure holds two Sparks one above the other, with an 18 mm gap between
them and 12 mm of space above and below. They rest on narrow rails along their
edges, so the open undersides stay in the airflow. At one end a 120 mm fan blows
air through the gaps past both machines, and the cap at the other end can take
a second fan. The fans need their own 12 V supply.

We tested it like this - two Sparks in it on NVIDIA's stock fan curve, against
two outside it with the 9,000 RPM fan floor. Under the same long load the two in
the enclosure stayed within a few degrees of the other two, with cooler NVMe
drives and no throttling. But that test changed two things together, the
enclosure and the fan control, so it isn't a measure of the enclosure alone.
Guide - [printed enclosure](docs/printed-enclosure.md).

### 3. Cap the GPU clock at 2,200 MHz

The Spark's GPU can boost as high as 3,003 MHz, but in our test everything above
2,200 MHz cost a lot of power and gave very little speed. So we stop it at
2,200 MHz with one `nvidia-smi` command, and a small systemd unit applies it
again at boot. Nothing else changes, and one command undoes it.

What we got in our test - GPU peak temperatures fell from 74–77 °C to 67–69 °C,
and busy GPU power from 44.8–49.1 W to 28.5–31.1 W. A single request generated
text only 1–2% slower. With sixteen requests at once the combined throughput
was 7.6% lower. Guide - [GPU clock cap](docs/gpu-clock-cap.md).

### 4. Raise the internal fan minimum to 9,000 RPM

In our test, under load the Spark's automatic fan control kept its two internal
fans at about 3,600 and 5,400 RPM. We set a floor of 9,000 RPM. That is, the fans
don't go below it, and the firmware can still spin them faster when it wants
to.

With the clock cap already on, the average GPU temperature fell from 60.0 to
52.7 °C and the NVMe drive from 48.6 to 42.9 °C. The price is fan noise and
setup work. The fan driver works only with the older EC firmware 3.5.8 and this
firmware has a bug that can stop the fans at idle, so it needs a workaround
too. Guide - [fan floor](docs/fan-floor.md).

### How to read these numbers

The clock-cap, fan-floor and enclosure numbers are from three separate
experiments, and the fan and enclosure tests ran with the cap already on. So
**please don't add them together** into one stock-to-final figure. The
clock-cap and fan-floor numbers are from four Sparks, and the enclosure test
from four other ones. Now all eight run the clock cap and six of them the fan
floor, the two in the enclosure keep NVIDIA's stock fan control. None of the
first four was throttling or shutting down before the changes. We simply wanted
them cooler, there was no failure to fix. Full tables, the method and what
didn't work are in [results](docs/results.md).

## How to try it on your own Spark

1. First measure, before you change anything, otherwise you have nothing to
   compare with.
2. Do the physical changes one at a time, and measure after each one.
3. Then try the clock cap. It needs no firmware change and it's easy to undo.
   Before you keep it, check temperatures, tokens per second and prefill time.
4. Do the fan floor last, and only after you've read its whole guide. It needs
   an EC firmware downgrade, and on the current EC 3.13.7 it doesn't work.
5. After each change check again - after a reboot, under long load and at idle.
   Look at both fan speeds and the EC clock, not only at the GPU temperature.

For the baseline, run this on the Spark from this checkout:

```sh
mkdir -p measurements
python3 scripts/thermal-sample.py --duration 60 --interval 2 > measurements/baseline.csv
python3 scripts/spark-fan status
```

Both commands only read, they change nothing. `thermal-sample.py` writes one CSV
row per sensor for each sample, that is every thermal zone, the GPU and each
NVMe drive. `spark-fan status` shows the EC firmware version, whether the EC
link is healthy, both fan speeds and the temperatures, and if something is
wrong it exits non-zero. If the fan driver isn't loaded, it can't tell you
whether a floor is set. Put longer runs into `measurements/` - git ignores it.

## What's in the repository

- Four guides in [docs/](docs/), one for each method. The bottom-cover guide
  also has the small external cooler that we tried for a while.
- The enclosure's two STL files, a render, a dimensioned drawing and five photos
  in [3d-print/](3d-print/README.md).
- `scripts/spark-fan` - a wrapper around the fan driver with checks.
- systemd units for the clock cap and the fan floor.
- `scripts/thermal-sample.py` - a sampler that only reads.
- Offline tests.
- [Measurement tables](results/) copied from our original experiment records.
- [Sources and credits](docs/sources.md).

`scripts/spark-fan` is the public version of the wrapper that we run on our
machines. Ours runs only on machines from a private list, and this one instead
asks you to register your Spark's hostname and serial once. The firmware,
EC-health and readback checks are the same. **Important - the public version
passes its offline tests but hasn't been run on a Spark yet.** The measurements
are from the original version on real hardware. There is no automatic installer
and no firmware flasher, every step is done by hand.

## Compatibility

We ran the fan procedure on NVIDIA DGX Spark with EC 3.5.8 SoC 2.158.15
kernel 7.0.0-1025-nvidia and the unmodified, signed dgx_ec_fan_control 0.1.4
module, commit `d121e06f0b62837632656ba95dc0d6445951142c` with Secure Boot on.
After a kernel update the module has to be built and signed again. Other
firmware combinations and partner GB10 machines we haven't tested.

## Development and license

```sh
python3 -m unittest discover -s tests -v
```

The code, documentation, STL designs, drawings and photos here are under the
[MIT license](LICENSE). The [upstream fan driver](https://github.com/christopherowen/dgx-spark-fan-control)
isn't included here, you install it separately and it has its own license. The
pinned version and credits are in the [source index](docs/sources.md#fan-control).
