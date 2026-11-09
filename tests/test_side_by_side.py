"""cellpose3 (Cellpose 3.1.0) and cellpose (Cellpose 4) installed and imported together."""

import subprocess
import sys
from importlib.metadata import version

import numpy as np
import pytest


def test_versions():
    import cellpose
    import cellpose3

    assert cellpose3.version == "3.1.0" == version("cellpose3")
    assert int(cellpose.version.split(".")[0]) >= 4


def test_packages_are_separate():
    import cellpose.models
    import cellpose3.models

    assert cellpose3.models is not cellpose.models
    assert cellpose3.models.CellposeModel is not cellpose.models.CellposeModel
    assert {"cyto3", "nuclei", "cyto2", "cyto"} <= set(cellpose3.models.MODEL_NAMES)
    assert "cpsam" in cellpose.models.MODEL_NAMES
    assert "cyto3" not in cellpose.models.MODEL_NAMES


def test_cellpose3_never_imports_cellpose():
    code = (
        "import sys, cellpose3, cellpose3.models, cellpose3.denoise, cellpose3.train;"
        "print(sorted(m for m in sys.modules if m == 'cellpose' or m.startswith('cellpose.')))"
    )
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    assert out.stdout.strip() == "[]"


def _discs():
    yy, xx = np.mgrid[:128, :128]
    image = np.zeros((128, 128), np.float32)
    for cy, cx in [(32, 32), (32, 96), (96, 32), (96, 96)]:
        image[(yy - cy) ** 2 + (xx - cx) ** 2 < 12**2] = 1.0
    return image


def test_cellpose3_segments_next_to_cellpose4():
    import cellpose.models
    import cellpose3.models

    masks, _, _ = cellpose3.models.CellposeModel(model_type="nuclei").eval(
        _discs(), diameter=24, channels=[0, 0]
    )
    assert masks.max() == 4
    assert cellpose.models.CellposeModel.__module__ == "cellpose.models"
