# cellpose3

A build recipe that installs [Cellpose](https://github.com/MouseLand/cellpose) 3.1.0 under
the import name `cellpose3`, so it can be installed in the same environment as Cellpose 4
(`cellpose`).

Cellpose 4 replaced the Cellpose 3 network with Cellpose-SAM and no longer runs the
Cellpose 3 models (`cyto3`, `cyto2`, `cyto`, `nuclei`). Both versions use the import name
`cellpose`, so one environment could only hold one of them. With this package:

```python
from cellpose3 import models as models3  # Cellpose 3.1.0: cyto3, cyto2, cyto, nuclei
from cellpose import models as models4   # Cellpose 4: cpsam

nuclei = models3.CellposeModel(model_type="nuclei")
cells = models4.CellposeModel(pretrained_model="cpsam")
```

For anything else about Cellpose, including documentation, issues and new versions, use the
upstream project: https://github.com/MouseLand/cellpose.

## What this repository contains

**No Cellpose source code.** It contains a build backend (`backend/cellpose3_backend.py`)
that, when the package is built:

1. downloads the official `cellpose-3.1.0-py3-none-any.whl` from PyPI (fixed URL) and checks
   its SHA-256;
2. copies its `cellpose/` package to `src/cellpose3/`;
3. renames the package's imports of itself from `cellpose` to `cellpose3` (18 lines), and
   makes `cellpose3/version.py` read the version of the `cellpose3` distribution;
4. builds the wheel with setuptools.

Nothing else is changed: this is an unmodified rename of Cellpose 3.1.0, kept only so that
it can be installed next to Cellpose 4. Segmentation masks are identical to a regular
Cellpose 3.1.0 install. Building needs network access to PyPI.

Pretrained weights are downloaded by Cellpose's own code to the same cache as Cellpose
(`~/.cellpose/models`, or `CELLPOSE_LOCAL_MODELS_PATH`). The Cellpose 3 and Cellpose 4
weight files have different names and do not collide. The command-line entry point is
`cellpose3`; the `cellpose` command stays with Cellpose 4.

## Install

```bash
pip install "cellpose3 @ git+https://github.com/cheeseman-lab/cellpose3@v3.1.0"
```

Cellpose 3.1.0 requires `numpy<2.1`; this package keeps that requirement.

## Credit and license

Cellpose is developed by Carsen Stringer and Marius Pachitariu (MouseLand, HHMI Janelia):
https://github.com/MouseLand/cellpose. Please cite Cellpose, not this package, as the
Cellpose authors ask:

- Stringer, C., Wang, T., Michaelos, M. & Pachitariu, M. (2021). Cellpose: a generalist
  algorithm for cellular segmentation. *Nature Methods* 18, 100-106.
- For `cyto3` or the image restoration models, also the Cellpose3 paper: Stringer, C. &
  Pachitariu, M. Cellpose3: one-click image restoration for improved segmentation.
- For human-in-the-loop training, also: Pachitariu, M. & Stringer, C. (2022). Cellpose 2.0:
  how to train your own model. *Nature Methods*.

The pretrained models are downloaded from the Cellpose servers at run time. The Cellpose
authors note that most of them are trained on data licensed CC-BY-NC.

Cellpose is distributed under the BSD 3-Clause license. `LICENSE` reproduces it unchanged
(Copyright © 2020 Howard Hughes Medical Institute), and the built package carries it. This
recipe is not affiliated with or endorsed by HHMI, MouseLand or the Cellpose authors.

## Tests

```bash
pip install ".[test]"
pytest
```

`tests/test_side_by_side.py` imports `cellpose3` next to Cellpose 4 in one process and runs a
small segmentation with `cellpose3`.
