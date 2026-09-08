# My Codex settings

複数の環境で使える Codex 設定です。共有設定の既定値はモデル `gpt-6-astra`、推論 effort `low`、sandbox `workspace-write` です。モデルの利用可否はアカウントや環境に依存します。`AGENTS.md` には、必要な作業を Luna（`gpt-5.6-luna`）へ委譲する方針を含みますが、委譲機能やモデルの利用を保証するものではありません。

## セットアップ

事前に Git、Codex、[uv](https://docs.astral.sh/uv/)、Bun をインストールし、Codex にログインしてください。

macOS / Linux：

```sh
git clone https://github.com/stella2211/my-codex-settings.git
cd my-codex-settings
./install.sh --dry-run
./install.sh
```

Windows（PowerShell）：

```powershell
git clone https://github.com/stella2211/my-codex-settings.git
cd my-codex-settings
.\install.ps1 --dry-run
.\install.ps1
```

`install.sh` と `install.ps1` は uv 経由で `tomlkit==0.15.1` を取得してインストーラーを実行します。agent-browser の導入を省略する場合は、どちらにも `--skip-agent-browser` を渡してください。適用先は `--codex-home`、環境変数 `CODEX_HOME`、既定の `~/.codex`（Windows は `$HOME\.codex`）の順で決まります。

通常のインストールは Bun で agent-browser をグローバルに追加し、ブラウザ本体をダウンロードします。初回はネットワーク接続が必要です。適用後は Codex を再起動し、新しい会話で使用してください。適用先に `AGENTS.override.md` がある場合は、`AGENTS.md` より優先されるため内容を確認してください。

## Windows の sandbox 回避策

Windows の Python でインストールすると、sandbox の動作が不安定な環境向けの暫定回避策として `approval_policy = "on-request"`、`approvals_reviewer = "auto_review"`、`sandbox_mode = "danger-full-access"` を自動適用します。環境の安定性を自動判定する機能はありません。macOS / Linux と WSL 内の Linux Python では `workspace-write` を使用します。

`danger-full-access` ではコマンドがワークスペース外のファイルを読み書きでき、意図しない変更・削除や機密情報へのアクセスのリスクがあります。承認設定はsandboxの隔離を代替しません。安定している環境では、適用後の `config.toml` を確認して `sandbox_mode = "workspace-write"` に戻してください。Windows で再度インストーラーを実行すると、回避策の値が再適用されます。

## 共有と更新

共有するのは `config.toml`、`AGENTS.md`、`model-instructions-long-waits.md` です。認証情報、環境変数の秘密値、履歴、メモリ、信頼設定、キャッシュは含めません。`config.toml` は既存設定へキー単位で再帰的にマージし、共有側の値を優先します。共有側にない既存キーは残ります。`AGENTS.md` は管理ブロックだけを更新し、その他のローカル指示を残します。

変更前の適用先ファイルは、適用先の `.codex-settings-backups/` にバックアップされます。更新するときは次のように実行してください。

```sh
git pull
./install.sh --skip-agent-browser
```

Windows では `git pull` の後に `.\install.ps1 --skip-agent-browser` を実行します。

## 待機設定

待機の最短値と既定値は 120 秒です。`AGENTS.md` の指示では、残り時間を見積もれる場合はその2倍を待機時間に指定し、見積もれない場合は既定値を明示します。

この設定は `multi_agent_v2` 使用時に適用されます。有効・無効は既存設定を維持するため、必要に応じて `[features.multi_agent_v2]` に `enabled = true` を追加してください。実際の待機時間はツールの上限に従います。

`model-instructions-long-waits.md` は組み込みの基本指示全体を置き換えます。定期報告を意味のある進捗報告に絞り、作業が進められない間の長時間待機を許容します。Codex の更新時は [上流プロンプト](UPSTREAM.md) との互換性を確認してください。

## Computer Use（任意）

macOS の ChatGPT デスクトップアプリで利用する場合は、ログイン済みの Codex から次を実行します。

```sh
./setup-computer-use.sh
```

このスクリプトは `computer-use` と `unified-computer-use` プラグインを追加します。画面収録やアクセシビリティなどの権限は、アプリの案内に従って設定してください。

`openai-bundled` マーケットプレイスで両プラグインを利用できる環境が必要です。

## 検証

```sh
uv run --no-project --with tomlkit==0.15.1 python -m unittest -v
```

## ライセンスと参照

- [LICENSE](LICENSE) — Apache License 2.0
- [NOTICE](NOTICE) — 著作権・帰属表示
- [UPSTREAM.md](UPSTREAM.md) — 上流資料と由来
