#!/usr/bin/env python3
"""Validate the imported WCAG 2.2 Understanding snapshot."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "understanding" / "wcag22"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validated_file(record: dict) -> bytes:
    path = ROOT / record["path"]
    require(path.is_file() and path.resolve().is_relative_to(DATA.resolve()),
            f"Missing or unsafe path: {path}")
    content = path.read_bytes()
    require(hashlib.sha256(content).hexdigest() == record["sha256"],
            f"Checksum mismatch: {path}")
    return content


def main() -> None:
    manifest = read(DATA / "manifest.json")
    documents = read(DATA / "documents.json")
    assets = read(DATA / "assets.json")
    items = read(ROOT / "data" / "items.json")
    wcag22_keys = {item["key"] for item in items if item.get("edition") == "2.2"}
    require(len(documents) == 218 and len(assets) == 186,
            "Understanding snapshot counts differ")
    require(manifest["counts"] == {"documents": 218, "image_references": 186,
                                   "documents_per_language": 109},
            "Manifest counts differ")
    require(Counter(d["language"] for d in documents) == {"ja": 109, "en": 109},
            "Document languages differ")
    require(Counter(a["language"] for a in assets) == {"ja": 93, "en": 93},
            "Image languages differ")
    require(len({(d["language"], d["filename"]) for d in documents}) == 218,
            "Duplicate documents")
    require(len({(a["language"], a["relative_path"]) for a in assets}) == 186,
            "Duplicate assets")
    require({d["filename"] for d in documents if d["language"] == "ja"} ==
            {d["filename"] for d in documents if d["language"] == "en"},
            "Unpaired document names")

    assets_by_path = {(asset["language"], asset["relative_path"]): asset
                      for asset in assets}
    references = set()
    for document in documents:
        require(document["item_key"] is None or document["item_key"] in wcag22_keys,
                f"Unknown item: {document['filename']}")
        content = validated_file(document)
        soup = BeautifulSoup(content, "lxml")
        local_images = {img.get("src", "") for img in soup.find_all("img")
                        if img.get("src", "").startswith("img/")}
        require(local_images == set(document["image_paths"]),
                f"Image references changed: {document['filename']}")
        for image in local_images:
            key = (document["language"], image)
            require(key in assets_by_path, f"Missing image URI: {key}")
            require(document["filename"] in assets_by_path[key]["referenced_by"],
                    f"Unlisted image reference: {key}")
            references.add(key)

    require(references == set(assets_by_path), "Unreferenced assets")
    for asset in assets:
        require(asset["relative_path"].startswith("img/"),
                f"Unexpected image path: {asset['relative_path']}")
        require(not (DATA / asset["language"] / asset["relative_path"]).exists(),
                f"Image bytes remain: {asset['relative_path']}")
        for field in ("source_url", "published_url"):
            parsed = urlparse(asset[field])
            require(parsed.scheme == "https" and parsed.netloc,
                    f"Invalid image URL: {asset[field]}")
    criteria = [item for item in items if item.get("edition") == "2.2"
                and item["kind"] == "success_criterion"]
    expected = {item["key"] for item in criteria}
    for language in ("ja", "en"):
        covered = {doc["item_key"] for doc in documents if doc["language"] == language}
        require(expected <= covered, f"Missing criteria in {language}")
    require(not list(DATA.rglob("img/*")), "Image bytes remain in dataset")
    print("Validated 218 documents, 186 image references, and no image files")


if __name__ == "__main__":
    main()
