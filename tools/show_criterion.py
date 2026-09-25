#!/usr/bin/env python3
"""Show one success criterion across WCAG/JIS editions and Understanding docs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
NUMBER_PATTERN = re.compile(r"[1-4]\.\d+\.\d+\Z")
EDITION_ORDER = {"wcag:2.2": 0, "wcag:2.1": 1, "wcag:2.0": 2,
                 "jis-x-8341-3:2016": 3}
RELATION_LABELS = {
    "same_number_in_later_edition": "後の版でも同じ番号（本文の同一性は未確認）",
    "removed_in_later_edition": "後の版で廃止",
    "corresponding_number_in_identical_standard": "一致規格の対応番号",
}
STATUS_LABELS = {
    "active": "その版で有効", "obsolete_in_2.2": "WCAG 2.2で廃止",
    "in_workbook": "手元資料から収録・正式照合未完了",
}
NAME_LABELS = {
    "official": "英語原文", "reference_translation": "WAIC参考訳",
    "historical_translation": "旧訳", "workbook_label": "手元資料",
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def plain_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for element in soup.find_all(("p", "div", "section", "aside", "li", "dt", "dd",
                                  "br", "h1", "h2", "h3", "h4", "h5", "h6",
                                  "blockquote", "pre", "tr", "td", "th")):
        element.insert_before(" ")
        element.insert_after(" ")
    return re.sub(r"\s+", " ", soup.get_text()).strip()


def lookup(number: str, data_dir: Path = DATA) -> dict:
    if not NUMBER_PATTERN.fullmatch(number):
        raise ValueError("達成基準番号は 2.4.6 の形式で指定してください")

    items = [item for item in read_json(data_dir / "items.json")
             if item["number"] == number and item["kind"] == "success_criterion"]
    if not items:
        raise LookupError(f"達成基準 {number} はデータセットにありません")
    keys = {item["key"] for item in items}
    names_by_key = defaultdict(list)
    for name in read_json(data_dir / "names.json"):
        if name["item_key"] in keys and name["value"] is not None:
            names_by_key[name["item_key"]].append(name)
    texts_by_key = defaultdict(list)
    for record in read_json(data_dir / "texts.json"):
        if record["item_key"] in keys:
            texts_by_key[record["item_key"]].append({
                "language": record["language"],
                "text": plain_text(record["html"]),
                "format": "plain_text",
                "source_id": record["source_id"],
                "source_ref": record["source_ref"],
            })
    relations = [record for record in read_json(data_dir / "relations.json")
                 if record["from"] in keys and record["to"] in keys]
    documents = [record for record in read_json(
        data_dir / "understanding/wcag22/documents.json")
                 if record["item_key"] == f"wcag:2.2:{number}"]
    sources = {record["id"]: record for record in read_json(data_dir / "sources.json")}

    editions = []
    used_sources = set()
    for item in sorted(items, key=lambda value: EDITION_ORDER.get(
            value["key"].rsplit(":", 1)[0], 99)):
        key = item["key"]
        names = names_by_key[key]
        texts = texts_by_key[key]
        used_sources.add(item["source_id"])
        used_sources.update(record["source_id"] for record in names + texts)
        editions.append({
            "key": key,
            "standard": item["standard"],
            "edition": item["edition"],
            "status": item["status"],
            "level": item.get("level"),
            "source_id": item["source_id"],
            "names": names,
            "texts": texts,
        })
    used_sources.update(record["source_id"] for record in relations)
    return {
        "number": number,
        "kind": "success_criterion",
        "editions": editions,
        "relations": relations,
        "understanding": sorted(documents, key=lambda record: record["language"]),
        "sources": {source_id: sources[source_id] for source_id in sorted(used_sources)},
    }


def format_text(result: dict) -> str:
    lines = [f"達成基準 {result['number']}"]
    for edition in result["editions"]:
        lines.append("")
        lines.append(f"{edition['standard']} {edition['edition']}"
                     f"  [{STATUS_LABELS.get(edition['status'], edition['status'])}]"
                     f"  レベル: {edition['level'] or '未設定'}")
        official_english = {name["value"] for name in edition["names"]
                            if name["language"] == "en" and name["status"] == "official"}
        for name in edition["names"]:
            if (name["status"] == "workbook_label" and name["language"] == "en"
                    and name["value"] in official_english):
                continue
            label = NAME_LABELS.get(name["status"], name["status"])
            if name.get("workbook_column"):
                label += f" / {name['workbook_column']}"
            lines.append(f"  名称 ({name['language']}; {label}): {name['value']}")
        if edition["texts"]:
            for body in edition["texts"]:
                lines.append(f"  本文 ({body['language']}): {body['text']}")
                lines.append(f"  本文出典: {body['source_ref']}")
        else:
            lines.append("  本文: 未収録")

    lines.extend(["", "版間の関係"])
    if result["relations"]:
        for relation in result["relations"]:
            label = RELATION_LABELS.get(relation["relation"], relation["relation"])
            lines.append(f"  {relation['from']} → {relation['to']}: {label}")
    else:
        lines.append("  記録なし")

    lines.extend(["", "WCAG 2.2 解説書"])
    if result["understanding"]:
        for document in result["understanding"]:
            lines.append(f"  {document['language']} 固定版ソース: {document['source_url']}")
            lines.append(f"  {document['language']} 公開ページ: {document['published_url']}")
    else:
        lines.append("  対応するページは未収録")
    lines.append("")
    lines.append("注: JIS名称は手元資料由来で、正式文書との照合は未完了です。")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("number", help="達成基準番号（例: 2.4.6）")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    try:
        result = lookup(args.number)
    except (ValueError, LookupError) as error:
        parser.exit(2, f"{error}\n")
    if args.format == "json":
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        print()
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
