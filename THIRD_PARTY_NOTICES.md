# 権利表示と出典

このリポジトリの `LICENSE`（MIT）は、プロジェクト独自のコード（`tools/`、`tests/`）と、プロジェクトが独自に作成した説明文・データ構造に適用します。第三者由来の規格本文、訳文、名称、解説書HTMLには適用しません。`data/` と `inputs/criteria-public.json` には由来の異なる内容が混在します。ファイル全体をMITライセンスのデータとして再配布する許諾を、このリポジトリは与えません。

## W3C

- `data/names.json`、`data/texts.json`、`data/catalog.csv` 等のWCAG英語名称・本文は、[WCAG 2.1](https://www.w3.org/TR/WCAG21/)と[WCAG 2.2](https://www.w3.org/TR/WCAG22/)に由来します。JSON版の利用条件は[W3Cの説明](https://github.com/w3c/wcag/tree/main/11ty/json#permission-to-use-with-attribution)を参照してください。出典を明示し、W3C由来の内容と追加情報を区別してください。
- `data/understanding/wcag22/en/` の英語解説書HTMLは、WAICが翻訳元として保存するW3C文書の固定版です。原文のバイト列を変更せずに保存しています。各文書の出典URLと版は `data/understanding/wcag22/documents.json` と `manifest.json` に記録しました。[W3C Document License](https://www.w3.org/copyright/document-license/)に従い、原文URL、著作権表示、文書のステータスを保持してください。

## WAIC

- `data/names.json`、`data/texts.json`、`data/catalog.csv` 等のWCAG 2.2日本語訳は、[WAIC「WCAG 2.2 日本語訳」](https://waic.jp/translations/WCAG22/)に由来します。翻訳者はWAIC翻訳ワーキンググループです。これは参考訳であり、正式版は[W3Cの英語版](https://www.w3.org/TR/WCAG22/)です。[WAICの翻訳文書の利用条件](https://waic.jp/license-for-translated-documents/)に従ってください。特に断片を再利用するときは、出典URL、翻訳者、文書のステータス、正式版に関する表示が必要です。個々の本文断片のURLは `data/texts.json` の `source_ref` にあります。
- `data/understanding/wcag22/ja/` の日本語解説書HTMLもWAICの翻訳文書です。原文のバイト列を変更せずに保存しています。各文書の出典URLと版は `data/understanding/wcag22/documents.json` と `manifest.json` に記録しました。利用条件は上記のWAICの説明を参照してください。

## JISと手元資料

- JIS X 8341-3:2016の名称は、手元のExcelから抽出した `inputs/criteria-public.json` に由来します。元のExcelファイルはこのリポジトリに置いていません。JIS本文も収録していません。[JISCのFAQ](https://www.jisc.go.jp/qa/a2-1.html)は規格番号・規格名称を許諾なしに記載できると説明していますが、達成基準ごとの名称について同じ扱いを明示しているとは断定できません。達成基準名の公開データとしての利用可否と権利者への確認は未完了です。JISCによれば著作権の帰属は規格によって異なり、引用・転載の相談は同FAQが案内する窓口から始められます。
- 未公開の予定名称は収録していません。

画像ファイルは収録せず、出典URIとハッシュのみを `data/understanding/wcag22/assets.json` に記録しています。ただし、解説書HTML内のインラインSVGは元の文書の一部として含まれます。
