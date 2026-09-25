#!/usr/bin/env python3
"""Fetch pinned sources, rebuild datasets, and check reproducibility."""

from __future__ import annotations

import argparse
import filecmp
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import build_dataset
import import_understanding


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CACHE = ROOT / ".cache"
UNDERSTANDING = Path("understanding/wcag22")
CORE_FILES = ("sources.json", "items.json", "names.json", "texts.json",
              "relations.json", "catalog.csv", "manifest.json")


def generate(target: Path) -> None:
    build_dataset.build(CACHE, build_dataset.PUBLIC_INPUT, target)
    sources = {lang: import_understanding.checked_repository(spec)
               for lang, spec in import_understanding.REPOSITORIES.items()}
    import_understanding.build_documents(target / UNDERSTANDING, sources)


def generated_paths(target: Path) -> set[Path]:
    return {path.relative_to(target) for path in target.rglob("*") if path.is_file()}


def check(target: Path) -> None:
    expected = generated_paths(target)
    actual = set(map(Path, CORE_FILES))
    actual.update(UNDERSTANDING / path.relative_to(DATA / UNDERSTANDING)
                  for path in (DATA / UNDERSTANDING).rglob("*") if path.is_file())
    if expected != actual:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(f"Generated file set differs; missing={missing[:5]}, extra={extra[:5]}")
    changed = [str(path) for path in sorted(expected)
               if not filecmp.cmp(target / path, DATA / path, shallow=False)]
    if changed:
        raise ValueError(f"Generated content differs: {changed[:10]}")
    subprocess.run([sys.executable, str(ROOT / "tools/validate_dataset.py")], check=True)
    subprocess.run([sys.executable, str(ROOT / "tools/validate_understanding.py")], check=True)
    print("Reproducible: generated files match the stored dataset")


def rebuild(target: Path) -> None:
    for filename in CORE_FILES:
        shutil.copy2(target / filename, DATA / filename)
    destination = DATA / UNDERSTANDING
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(target / UNDERSTANDING, destination)
    subprocess.run([sys.executable, str(ROOT / "tools/validate_dataset.py")], check=True)
    subprocess.run([sys.executable, str(ROOT / "tools/validate_understanding.py")], check=True)
    print("Rebuilt the dataset from pinned sources")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("fetch", "check", "rebuild"))
    args = parser.parse_args()
    if args.command == "fetch":
        build_dataset.fetch_sources(CACHE)
        for filename in build_dataset.SOURCE_FILES:
            build_dataset.source_bytes(CACHE, filename)
        import_understanding.fetch_repositories()
        print("Pinned sources are available in .cache/")
        return
    with tempfile.TemporaryDirectory(prefix="wcag-jis-build-") as temporary:
        target = Path(temporary) / "data"
        generate(target)
        if args.command == "check":
            check(target)
        else:
            rebuild(target)


if __name__ == "__main__":
    main()
