#!/usr/bin/env python3
"""Import pinned WCAG 2.2 Understanding documents and image references."""

from __future__ import annotations

import hashlib
import json
import mimetypes
import shutil
import subprocess
import tempfile
from collections import defaultdict
from datetime import date
from pathlib import Path, PurePosixPath

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "understanding" / "wcag22"
REPOSITORIES = {
    "ja": {
        "name": "waic/wcag22",
        "commit": "4c9eeeec7f284a946e4dfa8df605d813e90e8589",
        "directory": ROOT / ".cache" / "waic-wcag22",
        "subdir": "understanding",
        "published_base": "https://waic.jp/translations/WCAG22/Understanding/",
        "license_url": "https://waic.jp/license-for-translated-documents/",
    },
    "en": {
        "name": "waic/w3c-wcag",
        "commit": "9b5c06adee5cb4a1ad403a410165140b6d77b24c",
        "directory": ROOT / ".cache" / "waic-w3c-wcag",
        "subdir": "wcag22/understanding",
        "published_base": "https://www.w3.org/WAI/WCAG22/Understanding/",
        "license_url": "https://www.w3.org/copyright/document-license/",
        "w3c_origin_commit": "8ce579b",
    },
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def checked_repository(spec: dict) -> Path:
    repo = spec["directory"]
    if not repo.is_dir():
        raise ValueError(f"Repository is missing: {repo}")
    commit = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
    ).strip()
    if commit != spec["commit"]:
        raise ValueError(f"Unexpected revision for {spec['name']}: {commit}")
    if subprocess.check_output(
        ["git", "-C", str(repo), "status", "--porcelain"], text=True
    ).strip():
        raise ValueError(f"Source repository has local changes: {repo}")
    return repo / spec["subdir"]


def referenced_image(src: str) -> str | None:
    # The source pages also contain a remote analytics pixel. It is not an
    # illustration in the document and must not be bundled.
    if not src.startswith("img/"):
        return None
    path = PurePosixPath(src)
    if path.is_absolute() or ".." in path.parts or len(path.parts) != 2:
        raise ValueError(f"Unsafe image reference: {src}")
    return src


def import_documents(output: Path) -> None:
    sources = {language: checked_repository(spec) for language, spec in REPOSITORIES.items()}
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="understanding-build-", dir=output.parent) as temporary:
        staging = Path(temporary) / "wcag22"
        build_documents(staging, sources)
        if output.exists():
            shutil.rmtree(output)
        staging.rename(output)


def build_documents(output: Path, sources: dict[str, Path]) -> None:
    output.mkdir(parents=True)
    items = json.loads((ROOT / "data" / "items.json").read_text(encoding="utf-8"))
    item_by_anchor = {
        item["anchor"]: item["key"]
        for item in items
        if item.get("edition") == "2.2" and item.get("anchor")
    }
    documents = []
    assets = []
    page_sets = {}

    for language, spec in REPOSITORIES.items():
        source = sources[language]
        html_files = sorted(source.glob("*.html"))
        if len(html_files) != 109:
            raise ValueError(f"Unexpected document count for {language}: {len(html_files)}")
        page_sets[language] = {page.name for page in html_files}
        target_root = output / language
        target_root.mkdir()
        references = defaultdict(set)

        for page in html_files:
            data = page.read_bytes()
            soup = BeautifulSoup(data, "lxml")
            image_paths = set()
            for image in soup.find_all("img"):
                image_path = referenced_image(image.get("src", ""))
                if image_path:
                    image_paths.add(image_path)
                    references[image_path].add(page.name)
            target = target_root / page.name
            target.write_bytes(data)
            documents.append({
                "language": language,
                "filename": page.name,
                "item_key": item_by_anchor.get(page.stem),
                "path": (OUTPUT / language / page.name).relative_to(ROOT).as_posix(),
                "source_url": f"https://github.com/{spec['name']}/blob/{spec['commit']}/{spec['subdir']}/{page.name}",
                "published_url": spec["published_base"] + page.name,
                "sha256": digest(data),
                "image_paths": sorted(image_paths),
            })

        for image_path, pages in sorted(references.items()):
            original = source / image_path
            if not original.is_file():
                raise ValueError(f"Broken image reference: {original}")
            data = original.read_bytes()
            assets.append({
                "language": language,
                "relative_path": image_path,
                "source_url": f"https://github.com/{spec['name']}/blob/{spec['commit']}/{spec['subdir']}/{image_path}",
                "published_url": spec["published_base"] + image_path,
                "sha256": digest(data),
                "mime_type": mimetypes.guess_type(image_path)[0],
                "referenced_by": sorted(pages),
            })

    if page_sets["ja"] != page_sets["en"]:
        raise ValueError("Japanese and English document names differ")
    if len(assets) != 186:
        raise ValueError(f"Unexpected image count: {len(assets)}")
    write_json(output / "documents.json", documents)
    write_json(output / "assets.json", assets)
    write_json(output / "manifest.json", {
        "collection": "WCAG 2.2 Understanding",
        "status": "draft_local; public_release_review_pending",
        "retrieved_on": date.today().isoformat(),
        "sources": [
            {key: spec[key] for key in ("name", "commit", "subdir", "published_base", "license_url")}
            | {"language": language}
            | ({"w3c_origin_commit": spec["w3c_origin_commit"]} if "w3c_origin_commit" in spec else {})
            for language, spec in REPOSITORIES.items()
        ],
        "counts": {"documents": len(documents), "image_references": len(assets),
                   "documents_per_language": len(page_sets["ja"])},
        "notes": [
            "Original HTML bytes are stored unchanged; referenced image bytes are not stored.",
            "Remote analytics pixels, external media and page-wide styles/scripts are not bundled.",
            "The Japanese translation is informative; the W3C English text is authoritative.",
            "Local image references in source HTML will not resolve in this dataset; use assets.json URLs.",
        ],
    })
    print(f"Imported {len(documents)} HTML documents and {len(assets)} image references")


def main() -> None:
    import_documents(OUTPUT)


if __name__ == "__main__":
    main()
