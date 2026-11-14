# ABS enclosure for two DGX Sparks

This is the owner's two-piece design, printed in ABS, for holding two Sparks with
space for air to pass around them. A 120 mm fan mounts to the body. The cap closes
the other end and can hold a second fan. The demonstration shows the printed
parts and fan placement; it does not show a completed loaded thermal comparison.

![Two-piece ABS enclosure](../3d-print/DGX_Spark_Duo_photo_02.jpg)

## Files and parts

- [Body STL](../3d-print/DGX_Spark_Duo_body.stl), one.
- [Cap STL](../3d-print/DGX_Spark_Duo_cap.stl), one for the closed arrangement.
- [Design preview](../3d-print/DGX_Spark_Duo_preview.png) and
  [dimensioned section](../3d-print/DGX_Spark_Plan.png).
- One 120 mm fan, optionally a second; the demonstrated model is ARCTIC P12 Pro PST.
- Suitable fan mounting hardware, external power supply and fan controller.
  The recording does not identify a completed wiring arrangement or screw length.

All photos and the four design files are together in [3d-print/](../3d-print/README.md).
The [print notes](../3d-print/README.md#print-settings) record the saved ABS slicer settings.

## How the airflow path is arranged

![Section through the two computers](../3d-print/DGX_Spark_Plan.png)

The section drawing specifies 12 mm above the upper Spark, an open 18 mm gap
between them, and 12 mm below the lower Spark. Narrow rails overlap each lower
edge by 5 mm. There is no solid middle shelf touching the broad underside of the
upper machine. A front baffle limits air bypassing the intended route; the
openings in the ends accommodate the fans and cables.

These are design dimensions, not measured clearances of every print. Check your
actual fit before loading the enclosure. The green rail highlights in the drawing
are explanatory; the whole body prints in one material.

## Assemble

1. Print the body and optional cap in ABS; inspect them for cracks, warped rails
   and rough edges. Remove brim material and confirm the cap fits the empty body.
2. Dry-fit the 120 mm fan. Choose mounting screws that secure it without reaching
   a computer or damaging the printed wall. Secure cables clear of the blades.
3. Shut both Sparks down and disconnect them. If following the
   [bottom-cover method](bottom-cover.md), remove only the decorative underside
   panels and keep them for restoration.
4. Fit the machines onto the intended edge supports without forcing them. Check
   the open gap, clearance around the exposed underside and access to ports.
   Route cables through the provided openings without pinching them under the cap.
5. Orient the external fan using its airflow arrow so air passes through the
   enclosure. If adding the opposite fan, orient both for the same through-flow;
   they should not blow against each other. Keep the Sparks' own vents unobstructed.
6. Fit the cap if using it. Power the external fans from a suitable supply and
   controller; this guide does not assume an accessible fan header on the Spark.
   Confirm airflow and cable clearance before powering the computers.
7. Start both machines, verify sensors, then run the same sustained workload as
   the baseline. Watch both NVMe drives and both machines, not only the cooler GPU.

The ARCTIC fan shown is rated for 12 V DC, 0.33 A, with a four-pin PWM connection.
Its 6.9 mmH₂O static-pressure rating is a manufacturer specification, not pressure
measured inside this enclosure. It is not a USB-powered fan. Source:
[ARCTIC P12 Pro PST specification sheet](https://www.arctic.de/media/2c/de/c6/1750758983/Spec_Sheet_P12_Pro_PST_EN.pdf)
(source notes in [the index](sources.md#external-enclosure-fan)).

## Verify the cooldown

Keep workload, room conditions, clock cap and internal-fan policy fixed. Compare
the previous placement, the case with one fan and, if needed, the case with two.
Record external fan settings and the settled temperature of each NVMe drive.

```sh
mkdir -p measurements
python3 scripts/thermal-sample.py --duration 900 --interval 2 > measurements/enclosure-one-fan.csv
# Repeat the same workload and sampling for the comparison configuration.
```

Extend the run if temperatures are still changing. Check noise and stable idle
operation too. There is no published enclosure delta yet; the separate internal
fan-floor result in [results.md](results.md) is not an enclosure benchmark.

## Undo

Shut down both computers and disconnect power to them and the external fans.
Remove the cap and lift out the machines without loading the cables or antennas.
Refit the decorative panels if desired, restore the previous placement and
recheck under load. No software setting is changed by assembling this enclosure.
