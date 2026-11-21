# DGX Spark Duo print files

Designed by Stepan Kandrushin - an ABS body and cap for two DGX Sparks, with
120 mm fans moving air past them. These are my original design files, not
rescaled. The photos are of the printed parts, and the render shows how the two
computers sit inside.

| File | Purpose |
| --- | --- |
| [DGX_Spark_Duo_body.stl](DGX_Spark_Duo_body.stl) | Main enclosure and support rails |
| [DGX_Spark_Duo_cap.stl](DGX_Spark_Duo_cap.stl) | Opposite end cap with optional fan mount |
| [DGX_Spark_Duo_preview.png](DGX_Spark_Duo_preview.png) | Design render with two computers |
| [DGX_Spark_Plan.png](DGX_Spark_Plan.png) | Section drawing, dimensions in mm |

![Printed enclosure](DGX_Spark_Duo_photo_01.jpg)

The photos are in this same directory: [assembled exterior](DGX_Spark_Duo_photo_01.jpg),
[body and cap](DGX_Spark_Duo_photo_02.jpg), [inside both parts](DGX_Spark_Duo_photo_03.jpg),
[opposite exterior](DGX_Spark_Duo_photo_04.jpg), [open body and rails](DGX_Spark_Duo_photo_05.jpg).

## Print settings

My saved slicer projects are set up for a Bambu Lab X1 Carbon with a 0.4 mm
nozzle and Generic ABS, and the settings are these:

| Setting | Body | Cap |
| --- | --- | --- |
| Layer height | 0.20 mm | 0.20 mm |
| Wall loops | 2 | 2 |
| Infill | 15% grid | 15% grid |
| Supports enabled | No | No |
| Brim | Outer, 5 mm | Outer, 10 mm |
| Nozzle setpoint | 270 °C | 270 °C |
| Textured plate profile setpoint | 90 °C | 105 °C |

This is just what my profiles were set to, not a general ABS recipe. Use what
suits your printer, filament and plate. There is no G-code here, so you slice
the STLs yourself. In the saved print orientations the body is taller than the
cap.

STL files don't store units, so import them as millimetres, and before slicing
check that the sizes match these (X × Y × Z in the saved orientation):

- Body: 172.0 × 152.5 × 193.8 mm, 3,730 triangles.
- Cap: 178.5 × 155.5 × 86.2 mm, 3,474 triangles.

These are the sizes of each part on its own, not of the assembled case. The
section drawing shows 12 mm of space above and below and an 18 mm open gap
between the two Sparks. Before you put a computer in, check how the print fits
and that the rails hold.

How to assemble it, how the air flows, how to measure and how to take it apart -
all this is in the [enclosure guide](../docs/printed-enclosure.md). The designs,
drawings and photos are under the repository's [MIT license](../LICENSE).
