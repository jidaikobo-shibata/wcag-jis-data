# WCAG・JIS参照データセット

WCAGとJIS X 8341-3を版ごとに参照し、日本語名称の変遷を追えるデータセットを検討するリポジトリです。将来のチェックリスト、報告書、MCPなどが同じデータを利用することを想定しています。

現在は[設計案](docs/dataset-proposal.md)に基づく最初のデータ本体を収録しています。[データの読み方](data/README.md)と[117項目の一覧](data/catalog.csv)から確認できます。個々のウェブページに対する判定規則は収録していません。

## 維持するための手順

Python 3とGitを使います。初回だけ仮想環境に依存ライブラリを入れます。

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

公開済みの名称だけを含む `inputs/criteria-public.json` を入力に使います。手元の `criteria.xlsx` は通常の再生成に不要です。次のコマンドは、規格資料と解説書リポジトリを記録済みの版で取得し、全データを一時ディレクトリに再生成して、保存済みのファイルとバイト単位で比較します。

```bash
.venv/bin/python tools/maintain.py fetch
.venv/bin/python tools/maintain.py check
```

意図的にデータを再生成するときは `rebuild` を使います。取得元や入力の版を更新する場合は、変更内容と利用条件を確認したうえで、スクリプト内のコミットID・ハッシュを更新してください。自動的に最新版へ追従する処理はありません。

```bash
.venv/bin/python tools/maintain.py rebuild
```

## 手元の入力資料

- `criteria.xlsx`：英語名、JIS X 8341-3:2016での名称、WCAG各版の訳語などを比較する手元の資料
- `icl.xlsx`：確認条件と検査項目を含む作業用テンプレート

これらはGitの追跡対象から除外しています。出典と公開可否を確認するまで、内容をそのまま公開データとして扱いません。公開用の名称入力を作り直す場合だけ、`tools/build_dataset.py --export-public-input` を使用し、差分に未公開の列が含まれないことを確認します。

## データ本体

`data/` には、WCAG 2.2の原則・ガイドライン・達成基準・適合要件の117項目、旧版とJIS X 8341-3:2016の項目、各名称、本文、対応関係を収録しました。W3C原文とWAIC訳の取得時点を固定しています。公開前のドラフトであり、JIS本文と `icl.xlsx` の検査手順は未収録です。

生成方法と収録範囲は[データのREADME](data/README.md)に記載しています。

WCAG 2.2解説書は、[日英の資料スナップショット](data/understanding/README.md)として別に収録しました。翻訳元の版、画像、出典、公開前の確認事項はそちらに記載しています。

## 参照先

- [WCAG 2.2（W3C）](https://www.w3.org/TR/WCAG22/)
- [WCAG 2.2日本語訳（WAIC）](https://waic.jp/translations/WCAG22/)
- [JIS X 8341-3:2016関連文書（WAIC）](https://waic.jp/guideline/jis-x-8341-3_2016/)

日本語訳は参照情報です。規格の正確な内容を確認するときはW3Cの英語原文を参照します。
