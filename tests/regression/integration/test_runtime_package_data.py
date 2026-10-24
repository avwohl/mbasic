"""Verify installed distributions retain the runtime used by the C compiler.

Requires the standard packaging build tools: build, setuptools and wheel.
"""
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_runtime_shim_in_sdist_and_wheel(tmp_path):
    source = tmp_path / "source"
    shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns(
        ".git", "build", "dist", "*.egg-info", "__pycache__", ".pytest_cache",
    ))
    result = subprocess.run(
        [sys.executable, "-m", "build", "--no-isolation"], cwd=source,
        text=True, capture_output=True, timeout=180,
    )
    assert result.returncode == 0, result.stdout[-3000:] + result.stderr[-3000:]
    expected = (ROOT / "runtime/strings/mb25_uc80_shim.mac").read_bytes()
    sdist, = (source / "dist").glob("*.tar.gz")
    with tarfile.open(sdist) as archive:
        member, = [name for name in archive.getnames()
                   if name.endswith("/runtime/strings/mb25_uc80_shim.mac")]
        assert archive.extractfile(member).read() == expected
    wheel, = (source / "dist").glob("*.whl")
    with zipfile.ZipFile(wheel) as archive:
        assert archive.read("src/runtime/strings/mb25_uc80_shim.mac") == expected
        assert "src/runtime/strings/mb25_string.c" in archive.namelist()
        assert "src/runtime/strings/mb25_string.h" in archive.namelist()
