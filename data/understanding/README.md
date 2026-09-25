# WCAG 2.2 解説書の資料スナップショット

`wcag22/ja/` にWAICの日本語訳、`wcag22/en/` にWAICが翻訳元として保管するW3C英語原文を収録しています。各言語109件のHTMLを元のバイト列のまま保存しました。各言語93件の画像は出典URIとハッシュだけを記録し、実データは収録していません。HTML内のインラインSVGはHTMLとともに保存されています。遠隔の解析用画像、動画、外部メディア、ページ全体のCSSやJavaScriptは収録対象外です。

`wcag22/manifest.json` に取得元リポジトリのコミットID、`documents.json` にページとWCAG項目の対応・ハッシュ、`assets.json` に画像の参照元URI・ハッシュ・参照ページを記録しています。英語原文はWAICが翻訳元として保管する版であり、現在公開中のW3C解説書と同じ版であるとは限りません。WAICの[原文保管リポジトリ](https://github.com/waic/w3c-wcag)は、解説書のW3C側の元コミットを `8ce579b` と記載しています。

## 利用条件と公開前の確認

- WAIC訳には[WAICの翻訳文書の利用条件](https://waic.jp/license-for-translated-documents/)が適用されます。文書URL、翻訳者、文書のステータス、正式版がW3C英語版である旨を表示してください。原文の訳注を残して全文転載する場合、WAICは文書URLの明記でよいと説明しています。
- W3C原文には[W3C Document License](https://www.w3.org/copyright/document-license/)が適用されます。原文URL、著作権表示、文書のステータスを保持してください。原文の改変や派生文書には制限があります。
- 画像の実データは再配布せず、出典URIだけを記録します。画像ごとの例外的な権利表示の確認は未完了です。このスナップショットは公開前のドラフトです。

収録したHTMLは出典保存用です。本文中の画像相対パスはローカルでは解決しません。画像は `assets.json` の出典URIから確認してください。HTMLには外部のスクリプトや解析用画像への参照も含まれるため、そのままウェブで配信したり、信頼済みHTMLとして画面に挿入したりしないでください。閲覧用画面を作る場合は、安全なHTMLの生成と出典表示を別に実装してください。

## 再取得と検証

一時キャッシュの `.cache/waic-wcag22` と `.cache/waic-w3c-wcag` に、`manifest.json` に記録したコミットをそれぞれチェックアウトしてから実行します。現在の取り込みスクリプトはコミットIDを固定し、違う版を自動で混ぜません。版を更新するときは日英の対応と利用条件を再確認してください。

```bash
python3 tools/import_understanding.py
python3 tools/validate_understanding.py
```
