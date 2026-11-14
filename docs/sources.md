# Sources

The guides rest on the original experiment records and the primary references below.
This repository links to the publishers and does not redistribute their pages,
third-party documentation or firmware binaries.

## Fan control

The external driver is Christopher Owen's
[dgx-spark-fan-control](https://github.com/christopherowen/dgx-spark-fan-control),
version 0.1.4, pinned to `d121e06f0b62837632656ba95dc0d6445951142c`, GPL-2.0-only.
It is installed separately, unchanged. The wrapper in this repository is adapted
from our own deployment wrapper; it is not a fork of the kernel driver.

| Reference | Used for |
| --- | --- |
| [Upstream README](https://github.com/christopherowen/dgx-spark-fan-control) | Driver identity, floors, compatibility and license |
| [Pinned installation guide](https://github.com/christopherowen/dgx-spark-fan-control/blob/d121e06f0b62837632656ba95dc0d6445951142c/docs/installation.md) | Signed manual build and MOK enrollment |
| [NVIDIA forum discussion, post 24](https://forums.developer.nvidia.com/t/dgx-spark-fans-stop-when-the-screen-goes-dark-or-running-from-ssh-box-gets-too-hot-to-touch-fire-hazard/378945/24) | Original report in post 22, NVIDIA response in post 24, old-EC idle defect and workaround |

## Clock cap

[NVIDIA's nvidia-smi manual](https://docs.nvidia.com/deploy/nvidia-smi/index.html)
defines graphics-clock locking and reset.

[Wild Pines AI's account](https://www.wildpines.ai/blog/your-dgx-spark-is-cooking-itself/)
prompted our clock-cap test. Its machines, workload and reported results are its
own; our numbers come from our separate measurements. We do not adopt its broad
overheating explanations or claim that our machines suffered the shutdowns
described there.

## Physical modifications and design

The cover and enclosure guides come from two demonstration videos by the owner:
decorative bottom-cover removal with a temporary external-cooler trial, and a
walkthrough of the owner's printed ABS two-Spark enclosure. The videos are not
published. The design files and five case photos are in
[3d-print/](../3d-print/README.md). Print settings were read from the owner's saved
slicer projects; printer-specific G-code is not distributed.

## External enclosure fan

The enclosure footage shows an ARCTIC P12 Pro PST. Its dimensions, supply rating
and quoted static pressure were checked against the
[manufacturer's specification sheet](https://www.arctic.de/media/2c/de/c6/1750758983/Spec_Sheet_P12_Pro_PST_EN.pdf).
These are specification values, not measurements of the completed enclosure.

## Firmware

The official capsules below are the LVFS downloads, with the SHA-256 recorded from
the machine's LVFS metadata. A checksum establishes the downloaded bytes; fwupd
must still validate the signed capsule against the selected device.

The [fwupd 2.0.20 command source](https://raw.githubusercontent.com/fwupd/fwupd/2.0.20/src/fu-util.c)
confirms `local-install FILE [DEVICE-ID|GUID]`.

| EC | Official capsule | SHA-256 |
| --- | --- | --- |
| 3.5.8 | [Download](https://fwupd.org/downloads/3f220245f0803c4927490d01a8403560687fe6a631ec17e2c2d7359f76c3bef1-ec_fused.cab) | `3f220245f0803c4927490d01a8403560687fe6a631ec17e2c2d7359f76c3bef1` |
| 3.13.7 | [Rollback download](https://fwupd.org/downloads/c3fab69bb1ef6d22e1a1d28a0bbc05319fb321bf81af4fd574349d2b0b23fa30-ec_fused.cab) | `c3fab69bb1ef6d22e1a1d28a0bbc05319fb321bf81af4fd574349d2b0b23fa30` |

## Our measurements

The [result tables](results.md) and the [CSV files](../results/) are transcribed
aggregates of the clock comparison, fan sweep and persistence records.
They contain no machine names, serial numbers, private addresses or service
endpoints. The raw sample logs are not published.
