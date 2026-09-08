# My Codex settings

個人用 Codex 設定を複数の環境で共有するリポジトリ。Codex 0.153.4 の設定を元に作成しています。

## セットアップ

事前に Git、Codex、uv、Bun をインストールしてください。Codex のログインと各 MCP の認証は移行先で行います。モデルの利用可否は移行先のアカウントに依存します。

```sh
git clone <このリポジトリのURL> my-codex-settings
cd my-codex-settings
./install.sh --dry-run
./install.sh
codex mcp login freee_mcp
```

`install.sh` は uv 経由で Python と tomlkit を使います。初回は依存取得にネットワークが必要です。通常実行では Bun で agent-browser をインストールし、ブラウザ本体も取得します。Linux でブラウザのシステム依存が不足する場合は、`agent-browser install --with-deps` を別途実行してください。

既に agent-browser を管理している場合や、設定だけ反映したい場合：

```sh
./install.sh --skip-agent-browser
```

別の Codex home に適用する場合：

```sh
./install.sh --codex-home /absolute/path/to/codex-home
```

適用先は `--codex-home`、環境変数 `CODEX_HOME`、`~/.codex` の順で決まります。適用後はアプリを再起動し、新規会話で読み込みを確認してください。

## 共有する内容

| ファイル | 内容 |
| --- | --- |
| `config.toml` | モデル、パーミッション、メモリ機能、待機設定、agent-browser/freee MCP |
| `AGENTS.md` | ネイティブ Luna への委譲、Bun/uv の利用、待機時間の決め方 |
| `model-instructions-long-waits.md` | 基本指示の置き換え。60秒ごとの報告・待機制限を調整 |

設定は TOML のキー単位で既存ファイルへ再帰的にマージします。共有側にある値が優先され、共有側にない既存設定は残ります。既存の秘密情報を含む設定を表示しません。共有側からキーを削除しても、適用先のキーは削除しません。

AGENTS.md は管理対象のブロックとして挿入し、再実行時はそのブロックを更新します。既存のローカル指示は残します。モデル指示ファイルはコピーで更新し、`model_instructions_file` は適用先の絶対パスに設定します。変更前のファイルは適用先へバックアップします。

`AGENTS.override.md` があると同じ階層の `AGENTS.md` は読まれないため、移行先に存在する場合は内容を確認してください。プロジェクト固有の AGENTS.md と競合する指示はプロジェクト側が優先されます。

## 待機設定

- 最短・既定の待機時間：120秒。
- AGENTS.md：推定残り時間の2倍を指定。不明なら既定時間を明示。
- Codex 0.153.4 の最大待機時間は1時間。これは1回の待機の上限です。
- `multi_agent_v2` の有効・無効は移行先の選択を維持します。この待機設定は V2 使用時に適用されます。CLI でも V2 を使う場合は、`[features.multi_agent_v2]` に `enabled = true` を追加してください。

参考：[待機対策の投稿](https://x.com/u1/status/2096890699883123119)、[0.153.4 の待機実装](https://github.com/openai/codex/blob/rust-v0.153.4/codex-rs/core/src/tools/handlers/multi_agents_v2/wait.rs)。

## Computer Use

Computer Use は端末のアプリ・権限に依存するため、通常のインストーラーから分けています。対応する macOS のデスクトップアプリをインストールし、`openai-bundled` マーケットプレイスが利用できる状態で実行します。

```sh
./setup-computer-use.sh
```

このスクリプトは `codex plugin add` で `computer-use` と `unified-computer-use` を導入します。移行先の配布版でプラグインが提供されない場合はエラーになり、デスクトップアプリ側で利用可否を確認する必要があります。画面収録やアクセシビリティ等の許可はアプリの案内に従って設定してください。別 home を使う場合は同じ `CODEX_HOME` を環境に設定して実行してください。

この環境の旧 `mcp_servers.computer-use`、`node_repl` の実行パスやプラグインキャッシュはコピーしません。Figma、Context7 等の他のプラグインは必要に応じて移行先で追加してください。

## 更新と Git

```sh
git pull
./install.sh --skip-agent-browser
```

設定を変えるときは、このリポジトリのファイルを編集してコミットしてください。実際の `~/.codex/config.toml` を丸ごとコピーすると秘密情報や端末固有設定が混入するため、必要なキーだけを反映します。`model_instructions_file` は組み込み基本指示全体を置き換えるため、Codex 更新時には公式のモデル指示との差分を確認してください。

認証情報、環境変数の秘密値、履歴、メモリ内容、プロジェクト信頼設定、アプリキャッシュ、スキルは共有しません。旧 delegate-luna スキルも含みません。

GitHub 等のリモートは別途作成して登録します。このリポジトリの初期セットアップでは公開・push は行っていません。

```sh
git remote add origin <privateリポジトリのURL>
git push -u origin main
```

## 検証

```sh
uv run --no-project --with tomlkit==0.15.1 python -m unittest -v
```

一時ディレクトリで既存設定・コメント・認証値の保持、再実行、バックアップ、待機フラグの変換、dry-run を検証します。通常のインストールによるブラウザ取得と移行先での Computer Use 動作は、その環境で確認してください。
