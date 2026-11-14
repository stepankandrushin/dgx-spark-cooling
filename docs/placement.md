# Placement and air conditioning

We moved the Sparks under the air conditioner. There is no controlled measurement isolating its effect,
so we cannot give it a temperature or throughput improvement.

## Reproduce and measure it

1. Photograph the arrangement and record room temperature near the air intakes.
   Keep the intake and exhaust paths clear and avoid one unit feeding hot exhaust
   into the next. This is placement guidance, not a claim that we tested a particular spacing.
2. Run your normal workload until GPU and storage temperatures settle. Record
   workload, clock settings, fan settings and temperatures.
3. Stop the workload before relocating machines. Put them on a stable, dry surface
   in the cooled room, away from condensate or dripping water. Use the room's cooled
   air; do not add ice, water or a sub-ambient cooling device.
4. Keep the same model, concurrency, cables, clock settings and fan policy. Repeat
   the load and compare settled readings, with room temperature recorded again.
5. Check genuinely idle operation as well. A cool room does not repair the EC 3.5.8
   idle fan-stop defect described in the [fan guide](fan-floor.md).

For each position, sample for at least 15 minutes; extend the run if NVMe temperature
is still changing:

```sh
mkdir -p measurements
python3 scripts/thermal-sample.py --duration 900 --interval 2 > measurements/position-a.csv
# Repeat the same load in the new position, saving position-b.csv.
```

NVIDIA lists an ideal operating environment of 5–30 °C and non-condensing humidity.
These are environmental specifications, not a target GPU temperature or an AC setpoint.
Source: [NVIDIA hardware guide](https://docs.nvidia.com/dgx/dgx-spark/hardware.html).

## Undo

Stop the workload and restore the earlier arrangement, keeping the vents clear.
No software setting changes with this method.

The other physical changes are [bottom-cover removal and a temporary external
cooler](bottom-cover.md), and the [printed enclosure with external fans](printed-enclosure.md).
There is no documented repaste or aftermarket internal-heatsink modification.
