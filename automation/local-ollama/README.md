# ミセミルWeb：ローカルAI連携（検証用）

検証環境限定の下書き生成です。現在のリポジトリはPublicなので、店舗データ・資料・Google OAuth認証情報・生成したドラフトをGitHubにアップロードしないでください。

## できること
- MacのQwen3 8B (Ollama) を localhost:11434 で起動・呼び出す
- Google Sheetsの「LP制作入力」「LP要件定義キュー」「LP要件定義レビュー」をOAuthで読み込む
- 制作許可・素材利用許可、情報の不足、作成済みドラフトを確認し、未確認案件は生成しない
- 許可済みの1件について、未承認ドラフトをE列に保存する（明示的に --write-one を指定したときだけ）

行わないこと：自動営業DM、顧客への連絡、デザイン承認、GitHub公開、契約や課金、OpenAI APIへの送信。

## 最初はローカルAIだけをテスト

Macのターミナルでこのリポジトリのディレクトリから:

    python3 automation/local-ollama/worker.py --test-local

これは架空の案件についてAIに回答させるだけです。GoogleログインもSheetsの書き込みも発生しません。

## Google Sheets接続（次のステップ）

1. Python 3.10.7以上を使用。
2. Google Cloudプロジェクトを作成し、Google Sheets APIを有効化。
3. Google Auth PlatformのOAuth同意画面を設定し、Desktop app用OAuthクライアントを作成。Externalでテスト中の場合はテストユーザーに自分のGoogleアカウントを登録する。
4. ダウンロードした credentials.json をMacの ~/.config/misemiru-local-worker/credentials.json にだけ保存する。チャットやGitHubには貼らない。
5. Google用ライブラリを導入：

       python3 -m pip install -r automation/local-ollama/requirements.txt

6. 環境変数 MISEMIRU_TEST_SHEET_ID に検証用スプレッドシートIDを設定。正式台帳は使わない。
7. 読み取りのみでOAuth・権限を確認：

       python3 automation/local-ollama/worker.py --check-sheets

8. 顧客情報の出典と許可を正しく記録した案件でだけ、明示的に：

       python3 automation/local-ollama/worker.py --write-one

## 安全ゲートの詳細

- 検証用ブック名と列名の完全一致を要求。
- 「LP制作入力」の制作許可と画像利用許可がともに確認済み。
- 「LP要件定義キュー」の状態が「要件定義レビュー準備」、不足情報なし、出典と確認日が入力されている。
- 「LP要件定義レビュー」の判定が未確認、次工程移行が不可、ドラフトが空欄。
- 保存直前に権限や入力を再確認（更新競合の完全保証ではないため、本運用では別途ロック／更新検証を追加する）。
- レビュー判定、次工程移行、GitHubなどは一切変更しない。
- 入力したURLをOllama自身が調べることはできず、外部調査の検証は別工程が必要。

### 注意
Google SheetsのOAuthスコープは spreadsheets（読み書き）で、Googleアカウント上の他のスプレッドシートへのアクセス権も要求します。コード内では検証用ブック名に限定していますが、OAuth許可自体が1ファイルに限定されるわけではありません。最初はテスト用のGoogleアカウントで試すとより安全です。

Google Sheetsとの自動同期を完全な無人運用にするためのlaunchd設定は、ローカルテストとOAuth確認後に段階的に導入します。現在は自動定期実行を追加していません。
