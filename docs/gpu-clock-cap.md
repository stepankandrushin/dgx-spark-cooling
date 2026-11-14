# Cap the GPU graphics clock at 2,200 MHz

This is the simplest software change we kept. It reduces the upper graphics clock
while leaving the lower end at 300 MHz. It is not a 2,200 MHz fixed-frequency lock,
a CPU cap or a board power limit.

## Measure the baseline

On the Spark, record `uname -r`, `nvidia-smi`, `fwupdmgr get-devices` and your model,
precision, context sizes and concurrency. Confirm that no earlier clock-cap service
or other tuning tool will change settings during the comparison.

```sh
mkdir -p measurements
python3 scripts/thermal-sample.py --duration 1200 --interval 2 > measurements/clock-stock.csv
```

Run this in a second terminal while executing your usual inference benchmark.
Our experiment used an idle baseline, roughly seven minutes of warm-up, then hot
decode, concurrent requests and long-prefill tests. Record throughput separately;
the temperature sampler does not generate inference or measure tokens per second.

## Apply, cool down, repeat

```sh
sudo nvidia-smi -lgc 300,2200
```

Let the machines return to within approximately 1 °C of their initial idle
temperatures, then repeat the identical warm-up and benchmark with a new CSV.
Keep room conditions and all other tuning unchanged. For a cluster, apply the
same setting to every participating Spark and collect each machine's readings.

During load, inspect:

```sh
nvidia-smi --query-gpu=temperature.gpu,clocks.gr,power.draw,utilization.gpu,clocks_event_reasons.active --format=csv -l 2
```

Our busy clocks held around 2,177–2,190 MHz. Idle still sometimes showed 2,405 MHz,
and the advertised maximum stayed 3,003 MHz. Neither idle reading proves the cap failed.
Inspect sustained loaded readings and the command's success status.

## Keep it across reboots

After comparing results, install the supplied unit from the repository root:

```sh
sudo install -m 0644 systemd/spark-gpu-clock-cap.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now spark-gpu-clock-cap.service
systemctl status spark-gpu-clock-cap.service --no-pager
```

The unit runs after nvidia-persistenced and before Docker. Ordering does not make
your inference service depend on successful capping; check the unit and loaded
clocks after reboot before resuming an unattended workload. Stop jobs and reboot
at a suitable time, then repeat both checks. A successful oneshot normally shows
`active (exited)`.

## What changed in our test

Four-machine GPU peak ranges fell from 74–77 to 67–69 °C. Busy GPU power fell from
44.8–49.1 to 28.5–31.1 W; this is GPU telemetry, not whole-machine wall power.
CPU-zone hot means fell 2.2–6.8 °C and NVMe hot means 1.0–3.9 °C.

Single-request decode slowed about 1–2%. Sixteen concurrent requests fell from
239.2 to 221.0 tokens/s, or 7.6%. Prefill took about 2–5% longer.
One CPU peak increased despite its mean falling. See [results](results.md) for scope.

## Undo

```sh
sudo systemctl disable --now spark-gpu-clock-cap.service
sudo nvidia-smi -rgc
```

The unit's stop command resets graphics clocks; the second command also covers
a cap applied manually before installing the unit. Verify stock behavior under load.
If you had a different intentional clock policy, restore that policy separately.

The command semantics come from [NVIDIA's nvidia-smi manual](https://docs.nvidia.com/deploy/nvidia-smi/index.html).
The [source index](sources.md#clock-cap) also credits the article that prompted our test.
