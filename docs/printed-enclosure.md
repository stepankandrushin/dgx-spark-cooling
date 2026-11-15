# ABS enclosure for two DGX Sparks

I designed this enclosure to hold two Sparks with a fan pushing air past both of
them. It prints in two ABS parts. The body holds the machines and a 120 mm fan.
The cap closes the other end and can take a second fan. Each Spark sits on rails
along its edges, so air passes above, between and below the machines. That
includes the undersides, if you've [removed the bottom covers](bottom-cover.md).

We haven't measured this enclosure on its own, so there's no before/after number
for it yet.

![Two-piece ABS enclosure](../3d-print/DGX_Spark_Duo_photo_02.jpg)

## What you need

- [Body STL](../3d-print/DGX_Spark_Duo_body.stl), printed once.
- [Cap STL](../3d-print/DGX_Spark_Duo_cap.stl), printed once if you want the
  closed version.
- One 120 mm fan, plus a second one if you like. I use the ARCTIC P12 Pro PST.
- Screws to mount the fan, and a 12 V supply for it. The fan doesn't run from
  USB, and you shouldn't count on a fan header inside the Spark. I wire mine
  straight to the 12 V supply with a DIY connector and leave the PWM wire
  unconnected, so it always runs at full speed. Add a fan controller if you want
  it slower and quieter.

The [design preview](../3d-print/DGX_Spark_Duo_preview.png), the
[section drawing](../3d-print/DGX_Spark_Plan.png), the photos and the
[print settings](../3d-print/README.md#print-settings) are all in
[3d-print/](../3d-print/README.md).

## How the air flows

![Section through the two computers](../3d-print/DGX_Spark_Plan.png)

The drawing shows 12 mm of space above the upper Spark, an open 18 mm gap
between the two, and 12 mm below the lower one. Narrow rails hold each machine
by its lower edges, with 5 mm of overlap. There is deliberately no shelf under
the upper Spark, so air can reach its whole underside. A baffle at the front
keeps air from going around the machines instead of past them. The openings at
the ends are for the fans and cables.

These are design dimensions. Your print can come out slightly different, so
check the fit before you put the computers in. The green rails in the drawing
are only highlighted. The whole body is one material.

## Assemble

1. Print the body and, if you want it, the cap. Check for cracks, warped rails
   and rough edges, remove the brim, and make sure the cap fits the empty body.
2. Try the fan in place first. Pick screws long enough to hold it but short
   enough not to reach a computer or crack the wall. Keep its cable away from
   the blades.
3. If you're removing the bottom covers, do it now and keep the panels.
4. Slide the machines onto the rails without forcing them. Check that the gap is
   open, the undersides have clearance and you can reach the ports. Run the
   cables through the openings so the cap doesn't pinch them.
5. Point the fan by the arrow on its frame so it blows through the enclosure.
   With a second fan, point both the same way so they don't fight each other.
   Don't block the Sparks' own vents.
6. Fit the cap if you use it. Connect the fans to their 12 V supply and check
   that air is moving and nothing touches the blades.
7. Check that both machines' sensors read normally, and run the same
   long workload you used for your baseline. Watch both machines and both NVMe
   drives, not just the GPU.

The ARCTIC P12 Pro PST is a 12 V DC, 0.33 A fan with a four-pin PWM connector.
ARCTIC rates its static pressure at 6.9 mmH₂O. That's the maker's figure, not
something we measured in the enclosure. See the
[ARCTIC P12 Pro PST specification sheet](https://www.arctic.de/media/2c/de/c6/1750758983/Spec_Sheet_P12_Pro_PST_EN.pdf)
and the [source notes](sources.md#external-enclosure-fan).

## Measure the difference

Keep the workload, room, clock cap and internal fan settings the same, and
compare three setups: how the Sparks stood before, the enclosure with one fan,
and, if you want, the enclosure with two fans. Write down the external fan
speed and the settled temperature of each NVMe drive.

```sh
mkdir -p measurements
python3 scripts/thermal-sample.py --duration 900 --interval 2 > measurements/enclosure-one-fan.csv
# Repeat the same workload and sampling for the setup you're comparing against.
```

If temperatures are still changing at the end, run longer. Also listen to the
noise and check that both machines behave normally at idle. Our
[fan-floor result](results.md) is about the Spark's internal fans, not this
enclosure.

## Take it apart

Take off the cap and lift the machines out without pulling on cables or pressing on the antennas.
Refit the bottom panels if you want, and put the Sparks back where they were.
Run the load check again. The enclosure changes no software settings.
