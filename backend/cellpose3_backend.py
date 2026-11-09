"""PEP 517 build backend that builds cellpose3 from the official Cellpose 3.1.0 wheel.

At build time it downloads cellpose-3.1.0-py3-none-any.whl from PyPI, checks its SHA-256,
copies the `cellpose` package to `src/cellpose3`, renames the package's own imports to
`cellpose3`, and hands over to setuptools. Nothing else in Cellpose is changed.
"""

import hashlib
import re
import shutil
import urllib.request
import zipfile
from pathlib import Path

from setuptools import build_meta as _setuptools

CELLPOSE_VERSION = "3.1.0"
WHEEL_URL = (
    "https://files.pythonhosted.org/packages/d8/c1/"
    "3b604ec69233b9b8343e1e0cddcacd47438b52c53cc6c9ea76d6d68eb8a5/"
    "cellpose-3.1.0-py3-none-any.whl"
)
WHEEL_SHA256 = "242dd1adc23183b6a03f879a79e4901e466693005fe7e3106e9776a560db3fc0"

ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / "src" / "cellpose3"
IMPORT_PATTERNS = (
    (re.compile(r"^(\s*)from cellpose(\.| import)", re.MULTILINE), r"\1from cellpose3\2"),
    (re.compile(r"^(\s*)import cellpose(\.|$| )", re.MULTILINE), r"\1import cellpose3\2"),
)


def get_requires_for_build_wheel(config_settings=None):
    """Return setuptools' build requirements; setuptools needs src/ to exist."""
    PACKAGE.parent.mkdir(exist_ok=True)
    return _setuptools.get_requires_for_build_wheel(config_settings)


def get_requires_for_build_editable(config_settings=None):
    """Return setuptools' editable build requirements; setuptools needs src/ to exist."""
    PACKAGE.parent.mkdir(exist_ok=True)
    return _setuptools.get_requires_for_build_editable(config_settings)


def get_requires_for_build_sdist(config_settings=None):
    """Return setuptools' sdist requirements; setuptools needs src/ to exist."""
    PACKAGE.parent.mkdir(exist_ok=True)
    return _setuptools.get_requires_for_build_sdist(config_settings)


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    """Generate src/cellpose3 from the upstream wheel, then build the wheel."""
    generate_package()
    return _setuptools.build_wheel(wheel_directory, config_settings, metadata_directory)


def build_editable(wheel_directory, config_settings=None, metadata_directory=None):
    """Generate src/cellpose3 from the upstream wheel, then build an editable wheel."""
    generate_package()
    return _setuptools.build_editable(wheel_directory, config_settings, metadata_directory)


def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):
    """Generate src/cellpose3 so setuptools finds the package, then write metadata."""
    generate_package()
    return _setuptools.prepare_metadata_for_build_wheel(metadata_directory, config_settings)


def prepare_metadata_for_build_editable(metadata_directory, config_settings=None):
    """Generate src/cellpose3 so setuptools finds the package, then write metadata."""
    generate_package()
    return _setuptools.prepare_metadata_for_build_editable(metadata_directory, config_settings)


def build_sdist(sdist_directory, config_settings=None):
    """Build a recipe-only sdist: the Cellpose code is fetched again when it is built."""
    shutil.rmtree(PACKAGE, ignore_errors=True)
    PACKAGE.parent.mkdir(exist_ok=True)
    return _setuptools.build_sdist(sdist_directory, config_settings)


def generate_package():
    """Write src/cellpose3: the upstream cellpose package with its own imports renamed."""
    if (PACKAGE / "__init__.py").exists():
        return
    wheel = _download_wheel()
    shutil.rmtree(PACKAGE, ignore_errors=True)
    with zipfile.ZipFile(wheel) as archive:
        for name in archive.namelist():
            if not name.startswith("cellpose/") or name.endswith("/"):
                continue
            target = PACKAGE / name[len("cellpose/") :]
            target.parent.mkdir(parents=True, exist_ok=True)
            data = archive.read(name)
            if name.endswith(".py"):
                text = data.decode("utf-8")
                for pattern, replacement in IMPORT_PATTERNS:
                    text = pattern.sub(replacement, text)
                if name == "cellpose/version.py":
                    text = text.replace('version("cellpose")', 'version("cellpose3")')
                data = text.encode("utf-8")
            target.write_bytes(data)
    leftover = [
        str(path.relative_to(PACKAGE))
        for path in PACKAGE.rglob("*.py")
        if re.search(r"^\s*(from|import) cellpose(\.| |$)", path.read_text(), re.MULTILINE)
    ]
    if leftover:
        raise RuntimeError(f"Imports of the cellpose package remain in: {leftover}")


def _download_wheel():
    """Download the upstream Cellpose wheel into build/ and check its SHA-256."""
    wheel = ROOT / "build" / WHEEL_URL.rsplit("/", 1)[-1]
    if not wheel.exists() or _sha256(wheel) != WHEEL_SHA256:
        wheel.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(WHEEL_URL) as response, open(wheel, "wb") as out:
            shutil.copyfileobj(response, out)
    digest = _sha256(wheel)
    if digest != WHEEL_SHA256:
        wheel.unlink()
        raise RuntimeError(
            f"Downloaded Cellpose {CELLPOSE_VERSION} wheel has SHA-256 {digest}, "
            f"expected {WHEEL_SHA256}."
        )
    return wheel


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
