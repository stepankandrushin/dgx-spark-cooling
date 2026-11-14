# Remove the decorative bottom cover

The first physical change is to remove the decorative plastic panel from the
underside of the Spark. In the demonstration it comes off by hand, exposing the
area identified as the NVMe drive and the Wi-Fi antennas. The purpose is to let
air move across that underside, especially around the storage area.

This is the outer decorative panel, not the metal chassis or the NVMe module.
No drive, antenna or internal heatsink is removed in this method. We do not have
an isolated before/after temperature result for the panel alone.

## Procedure

1. Record a baseline under your usual sustained workload, including NVMe
   temperature. Then shut the Spark down, disconnect power and let it cool before
   handling the underside.
2. Support the machine on a clean, stable surface. Release the decorative bottom
   panel gently by hand, as shown in the demonstration. Keep the panel for undo.
   The recording does not establish a universal latch pattern: if it resists,
   inspect the attachment rather than forcing it or prying near electronics.
3. Leave the drive, antenna assemblies and metal chassis in place. Keep hands,
   tools and loose metal away from the exposed area.
4. Support the chassis on stable edges or the designed enclosure rails, leaving
   air space below it. Do not rest the exposed underside directly on a tabletop
   or block it with a solid shelf. The [two-Spark enclosure](printed-enclosure.md)
   provides edge supports and an open central gap.
5. Reconnect, run the same workload with the same clock/fan settings, and record
   settled temperatures. Monitor storage as well as the GPU; removing a panel
   does not itself create airflow.

## Temporary external cooler

The demonstration also shows a small external cooler tried against the underside.
The owner describes it as helping a little and as a temporary arrangement, not a
required part once the enclosure provides airflow. There is no controlled delta,
power measurement or validated mounting procedure for it. We therefore record it
as a trial, not a repeatable kit or a measured substitute for the enclosure.

## Measure the cooldown

Capture each configuration under the same sustained load, with room temperature,
placement, clock cap and internal-fan settings recorded. Keep a baseline run and
an after-change run; wait longer if the NVMe temperature is still trending.

```sh
mkdir -p measurements
python3 scripts/thermal-sample.py --duration 900 --interval 2 > measurements/cover-on.csv
# Shut down, remove the decorative panel, then repeat the same workload.
python3 scripts/thermal-sample.py --duration 900 --interval 2 > measurements/cover-off.csv
```

The script samples while your workload runs separately. Compare the settled part
of each run; do not compare a loaded machine with an idle one. Keep physical-test
results separate from the [existing clock and fan measurements](results.md).

## Undo

Shut down and disconnect power. Remove any temporary cooler, refit the original
decorative panel without trapping cables or disturbing the antenna assemblies,
and restore the previous stable placement. Repeat the same load check.
