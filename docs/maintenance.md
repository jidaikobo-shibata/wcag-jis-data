# データセットの維持

この文書は、固定した出典からデータを再取得し、保存済みの結果と照合する手順をまとめたものです。収録範囲は[データのREADME](../data/README.md)、利用条件は[権利表示と出典](../THIRD_PARTY_NOTICES.md)を参照してください。

## 準備

Python 3とGitを使います。初回だけ仮想環境に依存ライブラリを入れます。

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

入力する名称は `inputs/criteria-public.json` に固定してあります。Excel原本は不要です。取得元のURL・SHA-256は `tools/build_dataset.py`、解説書リポジトリのコミットIDは `tools/import_understanding.py` に記録しています。

## 再取得と検証

`fetch` は記録済みの版を `.cache/` に取得します。`check` は一時ディレクトリに全データを再生成し、保存済みのファイルとバイト単位で比較してから検証とテストを実行します。`check` は `data/` を書き換えません。

```bash
.venv/bin/python tools/maintain.py fetch
.venv/bin/python tools/maintain.py check
```

`fetch` は、取得元の内容が記録済みのハッシュやコミットIDと異なる場合に停止します。キャッシュ内のGitリポジトリが別のコミットや未保存の変更を含む場合も停止します。

## 意図的な更新

入力や出典の版を更新するときは、変更内容、日英の対応、利用条件を確認したうえで、ハッシュとコミットIDを更新します。その後、次のコマンドで `data/` を再生成します。`rebuild` は既存の生成データを置き換えます。

```bash
.venv/bin/python tools/maintain.py rebuild
.venv/bin/python tools/maintain.py check
```

差分では、名称、本文、項目の状態、出典URL、文書件数と画像参照を確認してください。検証スクリプトが通っても、訳語の正確性や公開条件まで保証するわけではありません。JIS達成基準名の公開条件は、引き続き確認が必要です。
