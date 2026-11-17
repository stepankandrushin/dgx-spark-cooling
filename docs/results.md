# Measurements and limitations

These numbers are copied from our original experiment records. They come from
four NVIDIA DGX Sparks serving DeepSeek inference. Six machines now run the same
clock and fan settings, but the other two weren't part of these tests. The raw
sample logs aren't published.

There are two experiments: the GPU clock cap and the internal fan floor. They
were run separately, so don't add their results together.

## Bottom cover, external cooler and printed enclosure

We have no measurements for these three. We never ran a before/after test for
removing the cover, for the small external cooler or for the ABS enclosure. Our
records don't say which physical setup each machine had during the two
experiments below either. So none of the numbers here belong to the cover or
the enclosure. The software comparisons also aren't a stock-case versus
printed-case test.

To measure them yourself, see the
[bottom-cover](bottom-cover.md#measure-the-difference) and
[enclosure](printed-enclosure.md#measure-the-difference) guides.

## GPU clock cap

Each run sent the same 91 requests, with no other API traffic. The machines
started idle, then about seven minutes of inference warmed them up before the
measured benchmark. Between the stock run and the capped run, all four cooled
back to within 1 °C of their starting idle temperature. Firmware and fan settings
stayed the same. We didn't control room temperature, and the capped run happened
later in the morning while the room was warming up.

| Metric | Stock | 2,200 MHz cap |
| --- | ---: | ---: |
| GPU peak range, four machines | 74–77 °C | 67–69 °C |
| Busy GPU power range | 44.8–49.1 W | 28.5–31.1 W |
| Prose decode, median of three | 64.2 tok/s | 63.4 tok/s |
| Code decode, median of three | 121.3 tok/s | 119.1 tok/s |
| JSON decode, median of three | 94.4 tok/s | 93.1 tok/s |
| Four requests together | 147.7 tok/s | 145.1 tok/s |
| Sixteen requests together | 239.2 tok/s | 221.0 tok/s |
| Approximately 100K-token prefill | 32.55 s | 33.42 s |

Average temperatures during the hot benchmark also fell: 2.2–6.8 °C in the CPU
zones and 1.0–3.9 °C on the NVMe drives. Not every peak fell, though. One
machine's CPU peak rose from 87.7 to 88.7 °C while its average dropped. We saw
no throttling or shutdowns before the cap either. Power is the GPU's
own reading, not measured at the wall. The sixteen-request loss is
`(221.0 / 239.2 - 1) * 100 = -7.61%` See [clock-performance.csv](../results/clock-performance.csv).

## Fan floor

The 2,200 MHz cap stayed on for the whole test. Sixteen continuous inference
streams heated the machines for 14 minutes on automatic. Then each floor ran
for ten minutes. Each number is the average of the last four minutes of its
interval across the four machines. The CPU column uses each machine's hottest
CPU-cluster zone. The second automatic run at the end shows how much things
drifted over the test.

| Requested floor | GPU °C | CPU °C | NVMe °C | Actual fans RPM | Aggregate tok/s |
| --- | ---: | ---: | ---: | --- | ---: |
| Automatic | 60.0 | 76.5 | 48.6 | 3,600 / 5,400 | 189 |
| 3,600 | 60.0 | 79.8 | 48.4 | 3,620 / 5,390 | 180 |
| 4,500 | 58.7 | 74.7 | 47.4 | 4,520 / 5,390 | 179 |
| 5,400 | 57.7 | 74.1 | 46.9 | 5,420 / 5,420 | 176 |
| 6,300 | 56.0 | 74.2 | 45.2 | 6,310 / 6,230 | 174 |
| 7,200 | 54.9 | 70.8 | 44.6 | 7,220 / 7,180 | 181 |
| 8,100 | 53.7 | 69.6 | 43.9 | 8,120 / 8,120 | 175 |
| 9,000 | 52.7 | 68.6 | 42.9 | 8,980 / 8,990 | 181 |
| 13,500 | 51.2 | 68.2 | 42.0 | 9,000 / 12,960 | 178 |
| Automatic again | 60.1 | 79.3 | 48.2 | 3,690 / 5,535 | 167 |

Against the first automatic run, 9,000 RPM is 7.3 °C cooler on the GPU, 7.9 °C on
the CPU and 5.7 °C on the NVMe drives. Against the average of both automatic
runs, the NVMe difference is 5.5 °C. If you quote a number, say which baseline it
uses. The [CSV](../results/fan-sweep.csv) also has TUNC and GPU power.

How far these numbers go:

- The CPU sensor is noisy and depends heavily on the workload.
- Other users' API traffic wasn't counted during this test, and the two
  automatic runs show different throughput. Treat the tok/s column with care.
- The test shows that faster fans mean lower temperatures. It doesn't show that
  they cost exactly zero performance, or that they make inference faster.
- The shared UPS reports power in 20 W steps, which is too coarse to say how
  much the fans use.
- We didn't measure noise or drive lifespan.

## Repeat the experiment

1. Write down the number of machines, firmware, kernel, model, quantization,
   context lengths, concurrency, room temperature, fan settings and clock
   settings. Stop unrelated requests. Use the same prompts and output-token
   limits in every run.
2. Start `scripts/thermal-sample.py` on every Spark in the test, with a clear
   file name for each. Keep a separate log of when each phase starts and of
   inference throughput and latency.
3. For a clock comparison, warm up the same way each time and compare while hot.
   Let temperatures come back close to the starting point before the next run.
4. For a fan sweep, keep clocks fixed and the workload running without a break.
   Test automatic, then 7,200 `set 50` 9,000 `set 66` optionally 13,500
   `set 100` and automatic again. Give each step at least ten minutes and use
   the settled last part. Run `sudo spark-fan auto` at the end even if the
   benchmark fails. If the floor service is running, a manual change overrides
   it until you restore it with `sudo systemctl restart spark-fan-floor`
5. Check for errors and missing values before averaging. Look at each machine,
   at averages and at peaks separately. A missing fan reading never means zero,
   and it never means the fan is fine.
6. To be more sure about cause and effect, repeat the steps in a different order.
   After any change, check that it survives a reboot and watch at least ten
   minutes of real idle.

## What these results don't show

- A combined improvement from adding the two experiments together.
- That our machines overheated before, or that the clock cap is free.
- Any measured benefit from removing the cover, the external cooler or the
  printed enclosure.
- That faster fans increase throughput, make SSDs last longer or are quiet.
- That the older EC is safe to run without its idle-fan workaround.
