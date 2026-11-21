# Cap the GPU graphics clock at 2,200 MHz

Of everything we did, this is the simplest change, and the easiest to undo. The
GPU can boost as high as 3,003 MHz, but in our test the clocks above 2,200 MHz
used a lot of power for very little extra speed. So the cap stops the GPU at
2,200 MHz. When there's little to do, it can still drop as low as 300 MHz.

That is, it doesn't lock the GPU at a fixed 2,200 MHz. And it doesn't touch the
CPU or set a board power limit.

## What it changed for us

On four Sparks under inference load:

- GPU peak temperatures fell from 74–77 °C to 67–69 °C.
- Busy GPU power fell from 44.8–49.1 W to 28.5–31.1 W. This is the GPU's own
  reading, not power at the wall.
- Average temperatures during the hot benchmark fell by 2.2–6.8 °C in the CPU
  zones and by 1.0–3.9 °C on the NVMe drives.
- A single request generated text about 1–2% slower. With sixteen requests at
  once it was 7.6% less, 221.0 instead of 239.2 tokens per second. Long prompts
  took about 2–5% longer to process.

On one machine the CPU peak went up slightly, even though its average fell. The
full table is in [results](results.md#gpu-clock-cap).

## Measure before you change it

Write down exactly what you're running, so you can repeat it one to one -
`uname -r` `nvidia-smi` `fwupdmgr get-devices` and your model, precision,
context sizes and concurrency. Make sure that no other clock-cap service or
tuning tool changes settings in the middle of the test.

In one terminal start the sampler, and in another one your usual inference
benchmark:

```sh
mkdir -p measurements
python3 scripts/thermal-sample.py --duration 1200 --interval 2 > measurements/clock-stock.csv
```

We did it like this - first the machines sat idle, then about seven minutes of
inference warmed them up, and then, while they were hot, we ran the decode,
concurrent-request and long-prompt tests. The sampler only records
temperatures, so log the tokens per second from your benchmark separately.

## Apply it, let it cool, repeat

```sh
sudo nvidia-smi -lgc 300,2200
```

Wait until the machines are back within about 1 °C of where they started at
idle. Then run the same warm-up and benchmark again into a new CSV, and change
nothing else. If you have several Sparks, apply the cap on all of them and
collect readings from each one.

While the load runs, watch the clocks:

```sh
nvidia-smi --query-gpu=temperature.gpu,clocks.gr,power.draw,utilization.gpu,clocks_event_reasons.active --format=csv -l 2
```

Under load ours held around 2,177–2,190 MHz. At idle `nvidia-smi` sometimes
still showed 2,405 MHz, and as the maximum it still lists 3,003 MHz. Neither of
these means the cap failed. Judge it by the clocks under sustained load and by
whether the command succeeded.

## Keep it after a reboot

After a reboot the cap is gone. If you want to keep it, install the systemd unit
from the repository root:

```sh
sudo install -m 0644 systemd/spark-gpu-clock-cap.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now spark-gpu-clock-cap.service
systemctl status spark-gpu-clock-cap.service --no-pager
```

It runs once at boot, after nvidia-persistenced and before Docker. When it has
worked, you see `active (exited)` in the status. But your inference service
starts even if the cap fails, so after a reboot check the unit and the clocks
under load before you leave the machine unattended. Choose a convenient time,
reboot once and check both.

## Undo

```sh
sudo systemctl disable --now spark-gpu-clock-cap.service
sudo nvidia-smi -rgc
```

Stopping the unit resets the clocks. The second command also clears a cap that
you set by hand before you installed the unit. After that check the clocks under
load. If you had your own clock settings before, put those back separately.

The commands are documented in [NVIDIA's nvidia-smi manual](https://docs.nvidia.com/deploy/nvidia-smi/index.html).
We tried this because of an article, and it's credited in the [source index](sources.md#clock-cap).
