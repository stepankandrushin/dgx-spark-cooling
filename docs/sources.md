# Sources

The guides are based on our own experiment records and on the references below.
We link to the publishers, and their pages, documentation and firmware files
aren't copied into this repository.

## Fan control

The external driver is Christopher Owen's
[dgx-spark-fan-control](https://github.com/christopherowen/dgx-spark-fan-control).
We use version 0.1.4 pinned to `d121e06f0b62837632656ba95dc0d6445951142c` its
license is GPL-2.0-only and you install it separately, unmodified. The
`spark-fan` wrapper here is the public version of the one we run on our
machines, it isn't a fork of the driver.

| Reference | Used for |
| --- | --- |
| [Upstream README](https://github.com/christopherowen/dgx-spark-fan-control) | Driver identity, floors, compatibility and license |
| [Pinned installation guide](https://github.com/christopherowen/dgx-spark-fan-control/blob/d121e06f0b62837632656ba95dc0d6445951142c/docs/installation.md) | Signed manual build and MOK enrollment |
| [NVIDIA forum discussion, post 24](https://forums.developer.nvidia.com/t/dgx-spark-fans-stop-when-the-screen-goes-dark-or-running-from-ssh-box-gets-too-hot-to-touch-fire-hazard/378945/24) | Original report in post 22 NVIDIA response in post 24 old-EC idle defect and workaround |

## Clock cap

Graphics-clock locking and reset are defined in
[NVIDIA's nvidia-smi manual](https://docs.nvidia.com/deploy/nvidia-smi/index.html).

We tried the clock cap because of
[Wild Pines AI's article](https://www.wildpines.ai/blog/your-dgx-spark-is-cooking-itself/).
Its machines, workload and results are its own, and our numbers come only from
our own measurements. We don't repeat its wider overheating explanations, and
the shutdowns it describes we didn't see on our machines.

## Physical modifications and design

The cover and enclosure guides are based on my own work on the machines. I
recorded it in two videos - one where I take off the bottom cover and try the
external cooler, and a walkthrough of the printed enclosure. The videos aren't
published. The design files and five photos are in
[3d-print/](../3d-print/README.md), the print settings come from my saved slicer
projects, and G-code isn't included.

## External enclosure fan

In the enclosure I use ARCTIC P12 Pro PST. Its size, power rating and static
pressure come from the
[manufacturer's specification sheet](https://www.arctic.de/media/2c/de/c6/1750758983/Spec_Sheet_P12_Pro_PST_EN.pdf).
That is, these are the maker's figures, not measurements in the enclosure.

## Firmware

The firmware images below are NVIDIA's official downloads from LVFS, and the
SHA-256 values come from the LVFS metadata on our machine. If the checksum
matches, it shows you downloaded the right file. fwupd still checks the image's
signature against your device when it installs it.

The syntax `local-install FILE [DEVICE-ID|GUID]` is confirmed by the
[fwupd 2.0.20 command source](https://raw.githubusercontent.com/fwupd/fwupd/2.0.20/src/fu-util.c).

| EC | Official capsule | SHA-256 |
| --- | --- | --- |
| 3.5.8 | [Download](https://fwupd.org/downloads/3f220245f0803c4927490d01a8403560687fe6a631ec17e2c2d7359f76c3bef1-ec_fused.cab) | `3f220245f0803c4927490d01a8403560687fe6a631ec17e2c2d7359f76c3bef1` |
| 3.13.7 | [Rollback download](https://fwupd.org/downloads/c3fab69bb1ef6d22e1a1d28a0bbc05319fb321bf81af4fd574349d2b0b23fa30-ec_fused.cab) | `c3fab69bb1ef6d22e1a1d28a0bbc05319fb321bf81af4fd574349d2b0b23fa30` |

## Our measurements

The [result tables](results.md) and the [CSV files](../results/) are summaries
copied from our records of the clock comparison, the fan sweep, the enclosure
test and the reboot checks. There are no machine names, serial numbers, private
addresses or service endpoints in them. We don't publish the raw sample logs.
