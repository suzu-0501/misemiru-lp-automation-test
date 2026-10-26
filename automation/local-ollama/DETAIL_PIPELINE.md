# 詳細なLP要件定義・デザイン定義のローカル生成（検証用）

## 目的・品質基準

実案件の hitoma サンプルLPに使った **要件定義書v0.5、デザイン定義書v1.2 と同等の詳細度を目標**にする。ただし、実案件固有の店舗情報・写真・ロゴ・配色はコピーしない。設計の章立てと確認プロセスを再利用する。

- 詳細な制作標準：../../quality-templates/requirements-standard.md と ../../quality-templates/design-standard.md
- 契約実績LPから抽象化した訴求・写真・CTA・レスポンシブの品質基準：./REFERENCE_QUALITY.md（実店舗素材や固有表現は転用しない）
- Qwen3:8b（Ollama localhost）による章ごとの生成
- 生成結果の検査と最大1回の自動修正
- **同じローカルモデル**によるPM視点／デザイナー兼FE視点の自己評価（人間や独立モデルによる監査ではない）
- 品質・情報不足・写真利用許可・承認の判断は人間が持つ
- 検証用ドラフトはMacのローカルフォルダに保存し、外部へ送信しない

## 動作範囲と費用

- 現在は **架空店舗 TEST-LP-001のみ**。実店舗の自動生成、シート同期、公開、PR作成、送信は行わない
- Google認証不要。OpenAI API料金不要。MacでOllamaを起動していること
- Macでスリープ中は生成されない
- 各章ごとにファイルを保存するため、中断したら同じコマンドで継続できる
- 検証用の結果に未確認の事実が残る可能性はあるため、人間の照合が必要

## 初回操作

ターミナルで次の2つを実行します。

    curl -fLsS "https://raw.githubusercontent.com/suzu-0501/misemiru-lp-automation-test/feature/local-ollama-bridge/automation/local-ollama/detail_pipeline.py" -o "$HOME/Downloads/misemiru_detail_pipeline.py"
    python3 "$HOME/Downloads/misemiru_detail_pipeline.py" --demo-requirements

出力先は:

    ~/Documents/MisemiruLocalAI/fictional-demo/

主な結果：

- requirements_draft.md （要件定義書・未承認）
- requirements_qa.json （必須章／根拠チェックの結果）
- requirements_ai_reviews.md （2ロールのAI自己評価）
- requirements_reference_qa.json （構成・写真・CTAなどの話題の有無と、人間の確認項目。自動合格ではない）
- requirements_chapter_XX.md （生成済みの各章）
- *_rejected.txt （検査で不合格の章。正式な仕様として使用しない）

## 要件定義の承認・デザイン定義

**人間が全資料と不足情報を確認した後だけ**：

    python3 "$HOME/Downloads/misemiru_detail_pipeline.py" --approve-demo-requirements

このコマンドは内容のハッシュを記録し、承認確認の入力があった場合にだけ保存します。

承認後にデザイン定義書へ進む場合：

    python3 "$HOME/Downloads/misemiru_detail_pipeline.py" --demo-design

承認後に要件定義書が変更されたら、デザイン生成は停止します。実装・写真生成・GitHub Pages公開はこのスクリプトでは行いません。

## 品質と課題

- 「見出しが存在する」は最低限の構造検査であり、内容や真偽の保証ではない
- 正式な実店舗ソースへの照合は未実装。**実店舗の事実を生成済みだと宣言してはいけない**
- Qwen3:8bは詳細な文書ほど漏れや誤りが起こり得るため、章ごとのチェック・承認が必須
- 同じモデルの複数ロール評価は専門家が2人いるわけではない
- 独自フォント・HEX・余白・セクション構図などは店舗の資料を受けて独自設計する
- 画像素材の権利とGitHub Pages公開可否は別のゲート。無確認で公開しない
- 次段階でGoogle Sheets検証用台帳とOAuth接続。production台帳は変更しない

## 補足：機密情報

このGitHubのリポジトリはPublicです。実店舗の未公開資料、店舗から受け取った画像、店舗情報の調査ファイル、OAuth tokens、要件定義書本文をアップロードしないでください。ローカルのDocumentsフォルダで管理してください。

## 保存済み要件の品質観点レビュー（AI生成なし）

```bash
python3 "$HOME/Downloads/misemiru_detail_pipeline.py" --audit-existing
```

既存の `requirements_draft.md` は変更せず、`requirements_reference_qa.json` を生成する。元のQAはバックアップ対象になる。キーワード言及の有無だけでは顧客の購買意欲・写真権利・事実・デザイン実機検査は判定できないため、必ず人間がレビューする。
