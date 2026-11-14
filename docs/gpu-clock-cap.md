# Cap the GPU graphics clock at 2,200 MHz

This is the simplest change we made, and the easiest to undo. The GPU can boost
as high as 3,003 MHz. In our test, the clocks above 2,200 MHz used a lot of
power for very little extra speed. The cap stops the GPU at 2,200 MHz. It can
still drop as low as 300 MHz when there's little to do.

It doesn't lock the GPU at a fixed 2,200 MHz. It also doesn't touch the CPU or
set a board power limit.

## What it changed for us

On four Sparks under inference load:

- GPU peak temperatures fell from 74–77 °C to 67–69 °C.
- Busy GPU power fell from 44.8–49.1 W to 28.5–31.1 W. That's the GPU's own
  reading, not power at the wall.
- Average temperatures during the hot benchmark fell 2.2–6.8 °C in the CPU
  zones and 1.0–3.9 °C on the NVMe drives.
- A single request generated text about 1–2% slower. Sixteen requests at once
  went from 239.2 to 221.0 tokens/s, 7.6% less. Long prompts took about 2–5%
  longer to process.

One machine's CPU peak went up slightly even though its average fell. The full
table is in [results](results.md#gpu-clock-cap).

## Measure before you change it

Record what you're running so you can repeat it exactly: `uname -r`,
`nvidia-smi`, `fwupdmgr get-devices`, and your model, precision, context sizes
and concurrency. Make sure no other clock-cap service or tuning tool will change
settings in the middle of the test.

Start the sampler in one terminal and your usual inference benchmark in another:

```sh
mkdir -p measurements
python3 scripts/thermal-sample.py --duration 1200 --interval 2 > measurements/clock-stock.csv
```

We let the machines sit idle first, warmed them up with about seven minutes of
inference, then ran decode, concurrent-request and long-prompt tests while they
were hot. The sampler only records temperatures, so log tokens per second from
your benchmark separately.

## Apply it, let it cool, repeat

```sh
sudo nvidia-smi -lgc 300,2200
```

Wait until the machines are back within about 1 °C of where they started at
idle. Then run the same warm-up and benchmark again into a new CSV. Change
nothing else. With several Sparks, apply the cap on all of them and collect
readings from each.

While the load runs, watch the clocks:

```sh
nvidia-smi --query-gpu=temperature.gpu,clocks.gr,power.draw,utilization.gpu,clocks_event_reasons.active --format=csv -l 2
```

Under load ours held around 2,177–2,190 MHz. At idle `nvidia-smi` sometimes still
showed 2,405 MHz, and it still lists 3,003 MHz as the maximum. Neither means the
cap failed. Judge it by the clocks under sustained load and by whether the
command succeeded.

## Keep it after a reboot

The cap is lost on reboot. If you want to keep it, install the systemd unit from
the repository root:

```sh
sudo install -m 0644 systemd/spark-gpu-clock-cap.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now spark-gpu-clock-cap.service
systemctl status spark-gpu-clock-cap.service --no-pager
```

It runs once at boot, after nvidia-persistenced and before Docker. When it has
worked, the status shows `active (exited)`. Your inference service still starts
even if the cap fails, so after a reboot check the unit and the loaded clocks
before you leave the machine unattended. Reboot once at a convenient time and
check both.

## Undo

```sh
sudo systemctl disable --now spark-gpu-clock-cap.service
sudo nvidia-smi -rgc
```

Stopping the unit resets the clocks. The second command also clears a cap you set
by hand before installing the unit. Check the clocks under load afterwards. If you
had your own clock settings before, put those back separately.

The commands are documented in [NVIDIA's nvidia-smi manual](https://docs.nvidia.com/deploy/nvidia-smi/index.html).
The article that got us to try this is credited in the [source index](sources.md#clock-cap).
