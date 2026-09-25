#!/usr/bin/env python3
"""Validate references, coverage, and the edition boundaries of generated data."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


DATA = Path(__file__).resolve().parents[1] / "data"


def read(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> None:
    sources, items, names, texts, relations, manifest = (
        read(name) for name in ("sources.json", "items.json", "names.json", "texts.json",
                          "relations.json", "manifest.json")
    )
    source_ids = {source["id"] for source in sources}
    item_keys = {item["key"] for item in items}
    require(len(source_ids) == len(sources), "Duplicate source IDs")
    require(len(item_keys) == len(items), "Duplicate item keys")
    require(len(items) == 378 and len(names) == 1031 and len(texts) == 329,
            "Dataset counts differ from the reviewed snapshot")
    require(len(relations) == 249, "Relation count differs from the reviewed snapshot")
    for kind, records in (("item", items), ("name", names), ("text", texts), ("relation", relations)):
        for record in records:
            require(record["source_id"] in source_ids, f"Unknown source in {kind}: {record}")
    for item in items:
        require(item["parent"] is None or item["parent"] in item_keys,
                f"Unknown parent: {item['key']}")
    for record in names + texts:
        require(record["item_key"] in item_keys, f"Unknown item: {record['item_key']}")
    for relation in relations:
        require(relation["from"] in item_keys and relation["to"] in item_keys,
                f"Broken relation: {relation}")

    counts = Counter((item["standard"], item["edition"]) for item in items)
    require(counts == {("WCAG", "2.2"): 117, ("WCAG", "2.1"): 95,
                       ("WCAG", "2.0"): 77, ("JIS X 8341-3", "2016"): 89},
            f"Edition counts differ: {counts}")
    criteria22 = [item for item in items if item["standard"] == "WCAG"
                  and item["edition"] == "2.2" and item["kind"] == "success_criterion"]
    require(len([item for item in criteria22 if item["status"] == "active"]) == 86,
            "WCAG 2.2 active success-criterion count differs")
    obsolete = [item for item in criteria22 if item["status"] == "obsolete_in_2.2"]
    require(len(obsolete) == 1 and obsolete[0]["number"] == "4.1.1",
            "WCAG 2.2 obsolete criterion differs")
    require(sum(item["kind"] == "success_criterion" and item["standard"] == "JIS X 8341-3"
                for item in items) == 61, "JIS 2016 criterion count differs")

    cells = [name["source_cell"] for name in names if name["source_id"] == "criteria-workbook"]
    require(len(cells) == 117 * 6 and len(set(cells)) == len(cells),
            "Not every workbook name cell was represented once")
    official_ja = {name["item_key"] for name in names if name["source_id"] == "waic-wcag22-ja"}
    require(len(official_ja) == 117, "WAIC names do not cover all WCAG 2.2 reference rows")
    require(all(text["html"] for text in texts), "Empty body in texts.json")

    with (DATA / "catalog.csv").open(encoding="utf-8", newline="") as stream:
        catalog = list(csv.DictReader(stream))
    require(len(catalog) == 117 and len({row["number"] for row in catalog}) == 117,
            "Catalog must contain 117 unique rows")
    require(manifest["counts"] == {"workbook_rows": 117, "items": len(items),
                                    "names": len(names), "texts": len(texts),
                                    "relations": len(relations)}, "Manifest counts differ")
    print("Validated 117 catalog rows, 378 items, 1031 names, 329 texts, 249 relations")


if __name__ == "__main__":
    main()
