# DGX Spark Cooling

Our NVIDIA DGX Spark cooling setup starts with removing the decorative bottom
cover and adding an ABS enclosure I designed for two Sparks, with 120 mm fans.
It also uses air-conditioned placement, a 2,200 MHz GPU clock cap, and a higher
minimum speed for the internal fans. This repository includes the printable
design, assembly notes, measured tradeoffs, verification and undo steps.

![The printed two-Spark enclosure](3d-print/DGX_Spark_Duo_photo_01.jpg)

**Print files:** [body](3d-print/DGX_Spark_Duo_body.stl) ·
[cap](3d-print/DGX_Spark_Duo_cap.stl) ·
[preview](3d-print/DGX_Spark_Duo_preview.png) ·
[section drawing](3d-print/DGX_Spark_Plan.png) ·
[photos and print notes](3d-print/README.md)

The measurements come from four Sparks running inference. The same clock and fan
settings are installed on six, but six-machine performance has not been measured.
The original four were not thermally throttling or shutting down in our tests.

## Choose a method

| Method | What we observed | Tradeoff | Instructions |
| --- | --- | --- | --- |
| Remove the decorative bottom plastic cover | Opens the underside around the NVMe area to moving air; demonstrated on camera, with no isolated temperature measurement | Exposed underside needs clearance and careful handling; a temporary external cooler was also tried | [Bottom cover](docs/bottom-cover.md) |
| Add the ABS two-Spark enclosure and external fans | Owner-designed, printed body and cap, with open spacing and 120 mm fan mounts | Needs suitable fan power/control and assembly; no isolated cooling measurement | [Printed enclosure](docs/printed-enclosure.md) |
| Move the machines under air conditioning | Used, but no isolated before/after temperature measurement | Room cooling and placement matter; no measured benefit claimed | [Placement](docs/placement.md) |
| Cap GPU graphics clocks at 2,200 MHz | GPU peaks 74–77 → 67–69 °C; busy GPU power 44.8–49.1 → 28.5–31.1 W | Single-request decode about 1–2% slower; sixteen-stream throughput 7.6% lower | [GPU clock cap](docs/gpu-clock-cap.md) |
| Hold a 9,000 RPM fan floor | With the clock cap already active: mean GPU 60.0 → 52.7 °C; NVMe 48.6 → 42.9 °C | More noise; requires a specific older EC firmware and an idle-fan workaround | [Fan floor](docs/fan-floor.md) |

Those temperature reductions are from separate experiments. **Do not add them
together** into a combined stock-to-final improvement. See the full
[results and measurement method](docs/results.md), including the unsuccessful attempts.

## Start here

1. Read the [bottom-cover guide](docs/bottom-cover.md) and
   [ABS enclosure guide](docs/printed-enclosure.md), including the printable files.
   Record a baseline, then compare each physical change separately.
2. Check [placement](docs/placement.md) and try the [clock cap](docs/gpu-clock-cap.md).
   The clock cap needs no firmware downgrade.
   Compare temperatures, tokens per second and prefill time before keeping it.
3. Consider the [fan floor](docs/fan-floor.md) only after reading its compatibility,
   installation and recovery steps. EC 3.13.7 does **not** support the driver pinned here.
4. Verify after reboot, under sustained load, and at genuinely idle operation.
   Confirm both fan RPM readings and the EC clock, not just GPU temperature.

Run these commands on the Spark, from this checkout:

```sh
mkdir -p measurements
python3 scripts/thermal-sample.py --duration 60 --interval 2 > measurements/baseline.csv
python3 scripts/spark-fan status
```

Both commands only read hardware. A nonzero status or a missing measurement is
something to investigate; an unloaded fan driver cannot prove the fan floor is automatic.
The sampler writes one row per sensor per sample, so it also records multiple NVMe drives.
Store longer runs in the git-ignored `measurements/` directory.

## What is included

- Five method guides, including the temporary external-cooler trial in the cover guide.
- Two original STL files, a design preview, a dimensioned section drawing and five case photos.
- A checked fan wrapper, systemd units, a read-only CSV sampler and offline tests.
- [Published measurement tables](results/) transcribed from the original experiment records.
- [Source index](docs/sources.md), with pinned upstream references and credits.

The wrapper adapts our deployed tool by replacing its private fleet allowlist with
an explicit local hostname/serial registration. Firmware, EC-health and readback
checks remain. **This public adaptation has offline test coverage; it has not yet
been exercised on a Spark.** The original installation and measurements are hardware-tested.
There is no automatic installer or firmware flasher.

## Compatibility

The fan procedure was validated on NVIDIA DGX Spark with EC 3.5.8, SoC 2.158.15,
kernel 7.0.0-1025-nvidia and the unchanged, signed dgx_ec_fan_control 0.1.4 module,
commit `d121e06f0b62837632656ba95dc0d6445951142c`. Secure Boot stays enabled.
The manual build must be repeated after kernel changes. This is a tested pairing,
not a qualification of other firmware combinations or partner GB10 machines.

## Development and license

```sh
python3 -m unittest discover -s tests -v
```

Original code, documentation, STL designs, drawings and case photos here use the [MIT license](LICENSE).
The separately installed [upstream fan driver](https://github.com/christopherowen/dgx-spark-fan-control)
has its own license; it is not vendored here. The
[source index](docs/sources.md#fan-control) gives the pinned version and credits.
