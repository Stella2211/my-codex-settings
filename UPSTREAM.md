# プロンプトの出典

`model-instructions-long-waits.md` は、OpenAI Codex の GPT-6 Astra 向けプロンプトをカスタマイズしたものです。Apache License 2.0 が適用されます（[LICENSE](LICENSE)・[NOTICE](NOTICE)）。

## 参照する上流ソース

- リポジトリ: [openai/codex](https://github.com/openai/codex)
- コミット: `0337192dfd10e12ac633dcd159fa6d6120dbfe11`
- ファイル: [codex-rs/models-manager/models.json](https://github.com/openai/codex/blob/0337192dfd10e12ac633dcd159fa6d6120dbfe11/codex-rs/models-manager/models.json)
- モデル: `gpt-6-astra`
- フィールド: `models` 配列の `slug == "gpt-6-astra"` の `model_messages.instructions_template`
- 抽出文字列のSHA-256（UTF-8、改行追加なし）: `152dfaeeb552876190962be1c12c93d426840ff12691f648261554a7675a6698`

## カスタマイズ内容

上流に対し、次の2か所を変更しています。

- **進捗報告**: 60秒ごとの報告義務を外し、意味のある進捗・状態変化・失敗・完了・入力要求を報告します。待機中に変化のない報告を繰り返しません。
- **長時間待機**: 60秒を超える待機の禁止を置き換え、独立した作業がない場合に長い待機を許容します。実際の待機時間はユーザーの指定とツールの上限に従います。

本文には上記以外の変更はなく、行末空白の除去と、ファイル先頭への出典・著作権・変更通知の追加を行っています。

## プロンプトを更新する場合

参照するコミットを固定して同じモデル・フィールドを取得し、上記2か所を適用してください。差分を確認し、このページのコミット・ハッシュとプロンプト先頭の出典を更新します。

再配布時は `LICENSE` と関連する帰属・変更通知を保持してください。
