# My Codex settings

`Stella2211`が Codex の設定を複数の端末で揃えるためのリポジトリです。共有設定の既定値はモデル `gpt-6-astra`、推論 effort `low`、sandbox `workspace-write` です。

## セットアップ

事前に Git、Codex、[uv](https://docs.astral.sh/uv/)、Bun をインストールし、Codex にログインしておく必要があります。

macOS / Linux：

```sh
git clone https://github.com/stella2211/my-codex-settings.git
cd my-codex-settings
./install.sh
```

Windows（PowerShell）：

```powershell
git clone https://github.com/stella2211/my-codex-settings.git
cd my-codex-settings
.\install.ps1
```

`install.sh` と `install.ps1` は uv 経由で `tomlkit==0.15.1` を取得してインストーラーを実行します。agent-browser の導入を省略する場合は、どちらにも `--skip-agent-browser` を渡してください。適用先は `--codex-home`、環境変数 `CODEX_HOME`、既定の `~/.codex`（Windows は `$HOME\.codex`）の順で決まります。

## Windows の sandbox 回避策

Windows 環境では Sandbox が不安定なことが多いため、デフォルトで `sandbox_mode = "danger-full-access"` を使用して Sandbox を無効化します。 macOS / Linux では `workspace-write` を使用します。

`danger-full-access` はコマンドがワークスペース外のファイルを読み書きでき、意図しない変更・削除や機密情報へのアクセスのリスクがあるため、自己責任で利用してください。

## 更新

更新時、 `config.toml` は既存設定へキー単位で再帰的にマージし、共有側の値を優先します。共有側にない既存キーは残ります。`AGENTS.md` は管理ブロックだけを更新し、その他のローカル指示を残します。

変更前の適用先ファイルは、適用先の `.codex-settings-backups/` にバックアップされます。更新するときは次のように実行してください。

```sh
git pull
./install.sh --skip-agent-browser
```

Windows では `git pull` の後に `.\install.ps1 --skip-agent-browser` を実行します。

## 待機設定

待機の最短値と既定値を 120 秒に上書きします。`AGENTS.md` で、残り時間を見積もれる場合はその2倍を待機時間に指定し、見積もれない場合は既定値を明示するよう指示します。

(この指示は Yuichi Uemura 氏の『[AstraでSubagent利用するとUsage消費ペースが激しすぎる問題への対策](https://x.com/u1/status/2096890699883123119)』を参考にさせていただきました。貴重な知見の共有に感謝します。)

`model-instructions-long-waits.md` は組み込みの基本指示全体を置き換えます。定期報告を意味のある進捗報告に絞り、作業が進められない間の長時間待機を許容します。Codex の更新時は [上流プロンプト](UPSTREAM.md) との互換性を確認してください。

## Computer Use（任意）

次を実行します。

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
