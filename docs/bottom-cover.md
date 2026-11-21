# Remove the decorative bottom cover

The bottom of the Spark is a decorative plastic panel, and behind it are the
NVMe drive and the Wi-Fi antennas. If you take the panel off, air can move
across this area, especially around the drive. It matters most when the Spark
sits in the [ABS enclosure](printed-enclosure.md), because there a fan moves air
through the gaps around it.

![Pulling the bottom cover off a DGX Spark by hand](images/bottom-cover-off.gif)

That's basically the whole job - the panel comes off with your fingers in a few
seconds, no tools. Only the outer panel comes off, the metal chassis, the drive,
the antennas and every heatsink stay where they are. Under it you will see
magnets. They don't hold the panel, they're there to catch the screws when you
unscrew them, so they don't roll away. But here nothing gets unscrewed.

We haven't measured the effect of the panel on its own.

## Take it off

1. First measure. Run your usual long workload and record the temperatures,
   including the NVMe drive, see [measuring](#measure-the-difference) below.
2. Put the Spark on its side and pull the panel off by hand, like in the clip
   above. Keep the panel for later. If it resists, first look at how it's held,
   and only then pull harder. Don't pry near the electronics.
3. Don't touch the drive, the antennas and the chassis. Keep tools and loose
   metal away from the open underside.
4. From now on the Spark stands on its edges with air space under it, for
   example on the enclosure's rails. Don't put it with the open underside flat
   on a table or a solid shelf. The point is that taking the panel off doesn't
   move any air by itself, it only helps if air can really reach the underside.
5. Run the same workload with the same clock and fan settings, and record the
   temperatures again. Watch not only the GPU but the drive too.

## The small external cooler

For a while I also had a small external cooler under the Spark. It helped a
little, but it was only a temporary solution. Once the enclosure moves air past
the machines, you don't need it. I didn't measure it and didn't work out a
proper way to mount it, so there is no guide for it.

## Measure the difference

Between the two runs everything else stays the same - workload, room
temperature, where the machine stands, clock cap and fan settings. Write all
this down. Start the sampler, run your workload next to it, and compare the
settled part of each run. If at the end the drive temperature is still
climbing, then run longer.

```sh
mkdir -p measurements
python3 scripts/thermal-sample.py --duration 900 --interval 2 > measurements/cover-on.csv
# Remove the panel, then repeat the same workload.
python3 scripts/thermal-sample.py --duration 900 --interval 2 > measurements/cover-off.csv
```

The sampler only records temperatures, it doesn't create any load, so run your
workload at the same time. Compare a run under load only with another run under
load, never with an idle one. And keep these results apart from our
[clock and fan measurements](results.md), they test different things.

## Put it back

Take away the extra cooler if you have one, press the panel back on so that it
doesn't trap cables or press on the antennas, and put the Spark back where it
was. Then run the same load check again.
