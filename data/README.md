# データの読み方

このディレクトリは、2026-09-25に取得した公式資料と、手元の `criteria.xlsx` から生成したドラフトです。[manifest.json](manifest.json)に件数を記録しています。原則・ガイドライン・達成基準・適合要件の117項目を、[catalog.csv](catalog.csv)で一覧できます。CSVの空欄の理由は `names.json` の `missing_marker` を参照してください。

| ファイル | 内容 |
| --- | --- |
| `sources.json` | URL、取得日、SHA-256、出典の状態 |
| `items.json` | 規格版ごとの項目、親子関係、レベル、廃止状態 |
| `names.json` | W3C英語名、WAIC日本語名、Excelの各列の名称と欠損記号 |
| `texts.json` | WCAG 2.1/2.2の英語本文、WCAG 2.2のWAIC日本語訳。HTML断片 |
| `relations.json` | 番号を介した版間・JISとの対応。本文の同一性を意味しない |
| `catalog.csv` | Excelの117項目を見渡すための表 |

## 収録範囲

- WCAG 2.2：117項目。達成基準は現行86件、廃止された4.1.1が1件。英語・日本語の本文を収録。
- WCAG 2.1：原則・ガイドライン・達成基準95項目。英語本文を収録。適合要件の節は未収録。
- WCAG 2.0：原則・ガイドライン・達成基準77項目。識別子、レベル、Excel由来の旧訳を収録。原文本文と適合要件の節は未収録。
- JIS X 8341-3:2016：Excelに名称がある89項目。本文は未収録。名称と項目の存在は手元の資料に依拠しており、JIS本文との照合は未完了。
- 「新JISでの名称（予定）」は予定名として収録。2027年版を想定しているが、年と名称は未確定として扱い、正式なJISの名称として使わない。`catalog.csv` の `planned_jis_ja` は原則・ガイドライン・達成基準に接尾語を加えた表示名。Excelの元の値は `names.json` の `workbook_column: planned_jis` に保持する。
- `icl.xlsx` の確認条件と検査手順は今回の参照データには未収録。

`4.1.1`はWCAG 2.2の資料に廃止項目として掲載されるため、項目自体を残し、`obsolete_in_2.2`にしています。現行86件の集計からは除いてください。

## 利用時の注意

W3Cの[英語原文](https://www.w3.org/TR/WCAG22/)が正式版です。[WAICの日本語訳](https://waic.jp/translations/WCAG22/)は参考訳で、翻訳者はWAIC翻訳ワーキンググループです。日本語訳の利用条件は[WAICの説明](https://waic.jp/license-for-translated-documents/)に従ってください。W3C JSONの利用条件は[W3Cリポジトリ](https://github.com/w3c/wcag/tree/main/11ty/json#permission-to-use-with-attribution)を参照してください。

`texts.json` の本文はHTML断片です。画面に表示するアプリでは信頼済みHTMLとして直接挿入せず、必要なタグだけを許すサニタイズを行ってください。リンクを含む断片は元文書のURLと併せて扱ってください。

このドラフトには、出典を未確認のExcelから転記した名称が含まれます。GitHubで公開する前に、`criteria.xlsx` の作成元、JISの名称、転載範囲を確認してください。

## 再生成

Python 3、`beautifulsoup4`、`openpyxl`を使います。ソースはスクリプト内のSHA-256に固定しているため、公開元が更新された場合は自動的に取り込まず停止します。更新するときは差分と出典を確認し、チェックサムを意図的に改めてください。

```bash
python3 tools/build_dataset.py --fetch
python3 tools/validate_dataset.py
```

手元の `criteria.xlsx` が必要です。`--fetch` で取得する公式資料はGitから除外された `.cache/` に保存されます。
