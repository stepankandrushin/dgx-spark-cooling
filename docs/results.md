# Measurements and limitations

These are transcribed experiment results, not a fresh benchmark. The numeric
tables cover four NVIDIA DGX Sparks serving DeepSeek inference. The settings are
installed on six machines, but the later two are not part of these comparisons.
Raw sample logs are not distributed here. The source record names and experiment
timing are retained in this repository's history entry.

## Bottom cover, temporary cooler and printed enclosure

The owner's demonstration shows removal of the decorative underside cover,
identifies the NVMe area and Wi-Fi antennas, and explains keeping airflow below
the machine. A temporary external cooler is shown and described as helping a
little; it has no controlled before/after result.

The second demonstration shows the ABS enclosure, a 120 mm fan, optional cap and
second fan, cable openings and internal supports. The section drawing specifies
an open 18 mm central gap and 12 mm clearance above and below the computers.
The footage demonstrates the enclosure's features; it does not show a completed
two-Spark installation running a thermal test. No temperature reduction is
attributed to the enclosure or cover removal in the tables below.

These demonstrations do not establish which physical configuration was present
in every earlier benchmark. Do not call the reported software comparisons a
stock-case versus printed-case test.

## GPU clock cap

Each comparison run had 91 requests and no unrelated API traffic. After an idle
baseline, roughly seven minutes of inference warmed the machines before the hot
benchmark. Between stock and capped runs, all machines cooled to within 1 °C of
their initial idle temperatures. The capped run happened later in a warming morning;
room temperature was not independently controlled. Firmware and fan policy were
unchanged within this comparison.

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

CPU-zone hot means fell 2.2–6.8 °C; NVMe hot means fell 1.0–3.9 °C. One CPU peak
rose from 87.7 to 88.7 °C while its mean fell, so “every peak fell” is false.
No pre-change thermal throttling or shutdown was observed. GPU telemetry power
is not a wall-plug measurement. Sixteen-stream throughput changed by
`(221.0 / 239.2 - 1) * 100 = -7.61%`.

## Fan floor

The 2,200 MHz cap stayed active throughout this separate experiment. Sixteen
continuous inference streams heated the machines for 14 minutes on automatic,
then each floor ran for ten minutes. Numbers use each interval's last four
minutes, averaged across the four machines; the CPU column is each machine's
hottest CPU-cluster thermal zone. The final automatic interval tests drift.

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

The [CSV](../results/fan-sweep.csv) includes TUNC and GPU power too. Comparing the
first automatic interval with 9,000 gives 7.3 °C lower GPU, 7.9 °C lower CPU and
5.7 °C lower NVMe. Comparing against the average of both automatic intervals
gives a 5.5 °C NVMe difference. Specify the baseline when quoting either.

The CPU sensor is noisy and workload-dependent. Other users' API traffic was not
counted during this sweep, and the two automatic throughput values differ. The
test establishes a cooling trend, not exactly zero performance effect or a fan
speed that increases inference throughput. No inference gain was demonstrated.
The shared UPS resolved power only in 20 W steps, too coarsely for fan-power claims.
No acoustic or drive-lifetime measurements were made.

## Repeat the experiment

1. Record machine count, firmware, kernel, model, quantization, context lengths,
   concurrency, room temperature, fan policy and clock settings. Stop unrelated
   requests. Use identical prompts and generated-token limits in both runs.
2. Start `scripts/thermal-sample.py` on every participating Spark. Label each file
   and keep a separate log of phase changes and inference throughput/latency.
3. For the clock comparison, warm each run identically and compare while hot.
   Let temperatures return close to the original baseline before the next run.
4. For the fan sweep, keep clocks fixed and workload continuous. Test automatic,
   7,200 (`set 50`), 9,000 (`set 66`), optionally 13,500 (`set 100`), then automatic
   again. Record at least ten minutes per phase, using settled trailing windows.
   Run `sudo spark-fan auto` at the end even if a benchmark fails. If the floor
   service is active, a manual change temporarily overrides it; restore the
   chosen boot floor with `sudo systemctl restart spark-fan-floor` afterwards.
5. Inspect errors and missing values before averaging. Compare per-machine values,
   means and peaks separately. Never treat a missing fan reading as zero or healthy.
6. Repeat phases in a different order if you need a stronger causal comparison.
   After changes, check reboot persistence and at least ten genuinely idle minutes.

## What not to claim

- A combined temperature improvement from adding the two separate tests.
- That our stock machines overheated, or that clock capping is free performance.
- That cover removal, the temporary cooler or the printed case has an isolated
  measured benefit in these records.
- That higher fans increase throughput, prove longer SSD life or are silent.
- That the older EC works safely without its idle-fan workaround.
