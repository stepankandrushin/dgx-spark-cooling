# Measurements and limitations

All numbers here are copied from our original experiment records. The clock-cap
and fan-floor tests ran on four NVIDIA DGX Sparks serving DeepSeek inference,
and the enclosure test on four other Sparks serving GLM. Now eight machines run
the clock cap and six of them the fan floor. We don't publish the raw sample
logs.

There are three experiments - the GPU clock cap, the internal fan floor, and the
printed enclosure on stock fans against the fan floor. They were run
separately, so please don't add their results together.

## Bottom cover and external cooler

For these two we have no measurements. We never ran a before/after test for
removing the cover or for the small external cooler, and our records don't say
which machines had their covers off in any of the experiments below. That is,
none of the numbers here belong to the cover or the cooler. The clock and fan
tests don't record where the machines stood either, so they aren't an enclosure
test.

If you want to measure the cover yourself, see the
[bottom-cover guide](bottom-cover.md#measure-the-difference).

## GPU clock cap

Each run sent the same 91 requests, and there was no other API traffic. The
machines started idle, then about seven minutes of inference warmed them up, and
only after that the measured benchmark ran. Between the stock run and the capped
run all four cooled back to within 1 °C of their starting idle temperature.
Firmware and fan settings stayed the same. We didn't control room temperature,
and the capped run was later in the morning, while the room was warming up.

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

Average temperatures during the hot benchmark also fell - by 2.2–6.8 °C in the
CPU zones and by 1.0–3.9 °C on the NVMe drives. But not every peak fell. On one
machine the CPU peak rose from 87.7 to 88.7 °C, while its average dropped. And
before the cap we saw no throttling or shutdowns either. Power is the GPU's own
reading, not measured at the wall. The sixteen-request loss is calculated as
`(221.0 / 239.2 - 1) * 100 = -7.61%` and the data is in
[clock-performance.csv](../results/clock-performance.csv).

## Fan floor

The 2,200 MHz cap stayed on for the whole test. First sixteen continuous
inference streams heated the machines for 14 minutes on automatic, then each
floor ran for ten minutes. Each number is the average of the last four minutes
of its interval across the four machines. For the CPU column we use each
machine's hottest CPU-cluster zone. The second automatic run at the end is there
to show how much things drifted over the test.

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
runs, the NVMe difference is 5.5 °C. So if you quote a number, say which
baseline it uses. The [CSV](../results/fan-sweep.csv) also has TUNC and GPU
power.

The limits of these numbers:

- The CPU sensor is noisy and depends a lot on the workload.
- Other users' API traffic wasn't counted during this test, and the two
  automatic runs show different throughput. So be careful with the tok/s column.
- The test shows that faster fans give lower temperatures. It doesn't show that
  they cost exactly zero performance, or that they make inference faster.
- The shared UPS reports power in 20 W steps, and that is too coarse to say how
  much the fans use.
- We didn't measure noise or drive lifespan.

## Printed enclosure against the fan floor

Four Sparks, none of which was in the tests above, ran the same load at the same
time, as two pairs:

- **In the enclosure** - two Sparks in the [printed enclosure](printed-enclosure.md)
  with both of its fans, on NVIDIA's current stock EC firmware 3.13.7 with its
  automatic fan curve. No fan driver, no floor and no idle-fan workaround.
- **With the floor** - two Sparks outside the enclosure, on EC 3.5.8 with the
  9,000 RPM floor.

All four had the 2,200 MHz GPU cap and the same 4 TB Samsung NVMe drive. What our
records don't say - whether the bottom covers were on or off, how fast the
enclosure's fans ran, and how the two outside it stood, beyond not being in it.

The load was GLM-5.3-Flash FP4 on vLLM. It doesn't fit into one Spark, so each
pair served it tensor-parallel over a direct 200 Gbit/s ConnectX-7 cable. Both
pairs got the same requests at the same time:

1. About ten minutes idle with the model loaded, and the first two minutes don't
   count.
2. 25 minutes of decode - four streams per pair, prose, code and JSON prompts,
   up to 1,500 output tokens each.
3. 15 minutes of prefill - four streams per pair, each a unique prompt of about
   18,000 tokens that the prefix cache couldn't reuse, up to 256 output tokens.
4. With the prefill load still on, fio on all four drives at once - 150 s of
   sequential writes, then 150 s of sequential reads, 1 MiB blocks at queue
   depth 32 with direct I/O, into a 32 GiB scratch file. Each drive took about
   1.35 TB of writes.

Each Spark logged its sensors every 10 s. The load columns are decode and
prefill, from five minutes after the load started until fio. The fio column is
the peak during fio on its own. CPU is the hottest CPU-cluster zone, NVMe is the
drive's composite temperature. Fan 2 stayed within 1% of fan 1 on the floor and
within 2% on stock. The head node of each pair also runs vLLM's API server and
scheduler. The room we logged only through the UPS's own temperature sensor,
and it read 25.8–26.3 °C through the run.

| Spark | Setup | Fan 1 RPM idle / decode / prefill / fio peak | CPU °C idle / load avg / load max / fio max | NVMe °C idle / load avg / load max / fio max | GPU °C idle / load avg / max |
| --- | --- | --- | --- | --- | --- |
| A head | floor | 9,000 / 9,000 / 9,000 / 9,000 | 41.2 / 76.1 / 85.5 / 92.1 | 38.9 / 52.3 / 53.9 / 67.8 | 39.0 / 61.6 / 67 |
| B worker | floor | 9,000 / 9,000 / 9,000 / 9,000 | 39.9 / 69.6 / 79.7 / 81.9 | 37.9 / 49.1 / 50.9 / 65.8 | 40.0 / 58.2 / 64 |
| C head | enclosure, stock | 1,840 / 2,364 / 2,369 / 2,946 | 39.7 / 75.7 / 89.1 / 87.7 | 37.1 / 48.5 / 49.9 / 61.9 | 39.1 / 60.8 / 66 |
| D worker | enclosure, stock | 1,882 / 1,901 / 1,906 / 2,403 | 42.2 / 72.5 / 77.4 / 81.8 | 37.2 / 47.6 / 49.9 / 62.9 | 40.4 / 60.5 / 68 |

Decode with four streams ran 70.1 tok/s in the floored pair's first ten minutes
and 71.1 in its last, and 70.8 and 71.0 in the enclosure pair. Prefill went from
1,680 to 1,740 prompt tok/s on the floored pair and from 1,650 to 1,709 on the
enclosure pair, and during fio it was 1,687 on both. No request failed. The
[CSV](../results/enclosure-vs-fan-floor.csv) also has TUNC and GPU power.

What it showed:

- **In the enclosure the stock curve was enough for this load.** If you compare
  head with head and worker with worker, the enclosure pair's CPU and GPU load
  averages came within 3 °C of the floored pair's, and its NVMe load averages
  were 1.5 and 3.8 °C cooler. Its fans ran 1,900–2,370 RPM under inference and
  2,400–2,950 during fio, far below the 9,000 RPM of the floor.
- **Nothing throttled.** GPU clock event reasons stayed clear, and under load the
  SM clock never fell below 2,171 MHz with the cap at 2,200 MHz. The CPU cooling
  devices never left state 0 and CPU frequency limits stayed at their maximum.
  fio wrote 9.1–9.3 GiB/s and read 13.5–13.6 GiB/s on every drive, the same on
  all four. Throughput was the same at the start and at the end.
- **The CPU of the head node has the smallest margin.** In the enclosure it
  peaked at 89.1 °C under load. Of its 267 samples under load, fio included, 17
  were at 85 °C or more, and it never reached 90 °C. The floored head peaked at
  92.1 °C during fio. It had 3 of 237 samples at 85 °C or more, two of them at
  90 °C or more during fio. Our monitoring warns at 99 °C, and the ACPI trip
  point is 104.8 °C.
- **The other margins are wide.** NVMe peaked at 63 °C in the enclosure and
  68 °C on the floor, while the drive's own warning and critical thresholds are
  83 °C and 85 °C. GPU peaked at 68 °C against a T.Limit of about 96 °C.
- **One fan reading of zero.** One 10 s sample on the floored head read fan 1
  at 0 RPM between two readings of 9,000 RPM. No temperature moved, and shortly
  after the fan status read 9,000 and 8,910 RPM. But the test's safety rule still
  stopped that pair's load, and it restarted about 2.5 minutes later. So the
  floored pair ran 20 minutes of decode against 25 for the enclosure pair, and
  its load windows start at the restart.

**What this doesn't show.** Here it's important to understand that the two
pairs differ in two things at once. One had the enclosure with NVIDIA's stock
firmware and fan curve, the other no enclosure, with the old firmware and the
floor. That is, the result belongs to this combination. It isn't the effect of
the enclosure alone, because the same machines weren't run outside it, and it
isn't the effect of the fan setting alone either. Also the pairs are different
machines, it was one run, and room temperature was logged, not controlled.

## Repeat the experiment

1. Write down the number of machines, firmware, kernel, model, quantization,
   context lengths, concurrency, room temperature, fan settings and clock
   settings. Stop unrelated requests. In every run use the same prompts and
   output-token limits.
2. Start `scripts/thermal-sample.py` on every Spark in the test, with a clear
   file name for each one. Separately keep a log of when each phase starts and
   of inference throughput and latency.
3. For a clock comparison, warm up the same way every time and compare while
   hot. Before the next run, let temperatures come back close to the starting
   point.
4. For a fan sweep, clocks stay fixed and the workload runs without a break.
   Test in this order:
   - automatic
   - 7,200 RPM `set 50`
   - 9,000 RPM `set 66`
   - optionally 13,500 RPM `set 100`
   - automatic again

   Give each step at least ten minutes and use the settled last part. At the end
   run `sudo spark-fan auto` even if the benchmark fails. If the floor service is
   running, a manual change overrides it until you restore it with
   `sudo systemctl restart spark-fan-floor`
5. Before averaging, check for errors and missing values. Look at each machine,
   at averages and at peaks separately. A missing fan reading never means zero,
   and it never means the fan is fine.
6. To be more sure about cause and effect, repeat the steps in a different
   order. After any change check that it survives a reboot, and watch at least
   ten minutes of real idle.

## What these results don't show

- A combined improvement from adding the experiments together.
- That our machines overheated before, or that the clock cap is free.
- Any measured benefit from removing the cover or from the external cooler.
- The effect of the printed enclosure alone, or of the stock fan curve alone -
  the enclosure test changed both at once.
- That faster fans increase throughput, make SSDs last longer or are quiet.
- That the older EC is safe to run without its idle-fan workaround.
