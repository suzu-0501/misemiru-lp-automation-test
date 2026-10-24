"""Offline tests for detailed LP pipeline. No Ollama or Google connection."""
import json
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import detail_pipeline as dp

class DetailedSpecTests(unittest.TestCase):
    def setUp(self):
        self.case = dp.demo_case()

    def test_ollama_streamed_reply(self):
        messages = [
            {"message": {"content": "接続テスト"}, "done": False},
            {"message": {"content": "成功"}, "done": True},
        ]
        stream = io.BytesIO("".join(json.dumps(m, ensure_ascii=False) + "\n" for m in messages).encode())
        with patch.object(dp, "urlopen", return_value=stream) as mock:
            result = dp.model_reply("system", "user", predict=30)
        self.assertEqual("接続テスト成功", result)
        sent = json.loads(mock.call_args.args[0].data)
        self.assertTrue(sent["stream"])
        self.assertFalse(sent["think"])

    def test_incomplete_ollama_stream_rejected(self):
        response = io.BytesIO(b'{"message":{"content":"draft"},"done":false}\n')
        with patch.object(dp, "urlopen", return_value=response):
            with self.assertRaisesRegex(RuntimeError, "未完了"):
                dp.model_reply("system", "user")

    def test_has_staged_specifications(self):
        self.assertEqual(6, len(dp.CHAPTERS["requirements"]))
        self.assertEqual(6, len(dp.CHAPTERS["design"]))
        self.assertTrue(all(len(titles)==2 for _,titles in dp.CHAPTERS["design"]))

    def test_fake_sheet_verified_rejected(self):
        self.assertTrue(dp.check_grounding("東京都渋谷区はシート確認済です", self.case))

    def test_unsupplied_hours_rejected(self):
        self.assertTrue(dp.check_grounding("営業時間：10:00〜22:00", self.case))

    def test_unsupplied_seating_rejected(self):
        self.assertTrue(dp.check_grounding("席数：15席です", self.case))

    def test_unsupplied_city_address_rejected(self):
        self.assertTrue(dp.check_grounding("住所：東京都港区芝公園2丁目", self.case))

    def test_fake_source_id_rejected(self):
        self.assertTrue(dp.check_grounding("営業時間【F999】", self.case))

    def test_unknown_values_not_treated_as_facts(self):
        self.assertEqual([], dp.check_grounding(
            "営業時間は未確認です。予約可否とInstagram URLは要質問です。", self.case))

    def test_real_case_cannot_run(self):
        real = dp.demo_case()
        real["fictional"] = False
        with self.assertRaises(RuntimeError):
            dp.only_fictional(real)

    def test_missing_heading_caught(self):
        errors = dp.check_chapter("短い", dp.CHAPTERS["requirements"][0][1], self.case)
        self.assertTrue(any("見出し欠落" in x for x in errors))


    def test_each_section_heading_is_code_controlled(self):
        def answer_without_heading(system, user, predict=1800):
            return ("未確認事項は質問する。観測していない情報を確認済みと書かない。"
                    "権利と情報の整合性を確認する。" * 18)
        with patch.object(dp, "model_reply", side_effect=answer_without_heading):
            draft, issues = dp.build_chapter(
                "requirements", dp.CHAPTERS["requirements"][0], self.case
            )
        self.assertEqual([], issues)
        for title in dp.CHAPTERS["requirements"][0][1]:
            self.assertIn("## " + title + "\n", draft)

    def test_unsafe_generated_section_rejected(self):
        def fake_assertion(system, user, predict=1800):
            return "店舗所在地は東京都渋谷区で公式サイト確認済です。" * 30
        with patch.object(dp, "model_reply", side_effect=fake_assertion) as m:
            draft, issues = dp.build_chapter(
                "requirements", dp.CHAPTERS["requirements"][0], self.case
            )
        self.assertTrue(issues)
        self.assertNotIn("東京都渋谷区", draft)
        self.assertEqual(4, m.call_count)

    def test_cached_section_survives_sibling_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            title = dp.CHAPTERS["requirements"][0][1][0]
            safe = "## " + title + "\n\n" + ("これは未確認であり、店舗情報は推測しません。" * 20)
            dp.save_text(root / "requirements_section_01_1.md", safe)
            with patch.object(dp, "generate_section", return_value=("bad", ["danger"])) as model:
                draft, issues = dp.build_chapter(
                    "requirements", dp.CHAPTERS["requirements"][0], self.case, root=root)
            self.assertIn(safe, draft)
            self.assertEqual(1, model.call_count)
            self.assertTrue(issues)

    def test_recover_old_rejected_section_without_ai_calls(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            title_a, title_b = dp.CHAPTERS["requirements"][3][1]
            safe_a = (
                "## " + title_a + "\n\n" +
                "承認済みの素材だけを使用する。これは承認が存在するという事実ではない。\n" +
                ("未確認の情報は要質問とする。確定の根拠がない事項は使わない。\n" * 15)
            )
            safe_b = "## " + title_b + "\n\n" + ("画像権利は未確認、要承認。\n" * 20)
            dp.save_text(
                root / "requirements_section_04_1_rejected.txt",
                "以前の安全検査結果：承認済みの条件表現を誤検出\n\n" + safe_a,
            )
            dp.save_text(
                root / "requirements_section_04_2.md", safe_b
            )
            with patch.object(dp, "generate_section") as model:
                draft, issues = dp.build_chapter(
                    "requirements", dp.CHAPTERS["requirements"][3],
                    self.case, root=root
                )
            model.assert_not_called()
            self.assertEqual([], issues)
            self.assertIn(safe_a, draft)
            self.assertIn(safe_b, draft)
            self.assertTrue(
                (root / "requirements_section_04_1.md").exists()
            )

    def test_recover_valid_section_from_rejected_chapter(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            title = dp.CHAPTERS["requirements"][0][1][0]
            safe = "## " + title + "\n\n" + ("要確認の設計案です。未確認の事実を追加しません。" * 18)
            dp.save_text(root / "requirements_chapter_01_rejected.txt",
                         "安全検査で差し戻し\n\n" + safe)
            with patch.object(dp, "generate_section", return_value=("bad", ["danger"])) as model:
                draft, issues = dp.build_chapter(
                    "requirements", dp.CHAPTERS["requirements"][0], self.case, root=root)
            self.assertIn(safe, draft)
            self.assertEqual(1, model.call_count)
            self.assertTrue((root / "requirements_section_01_1.md").exists())

    def test_approval_policy_is_not_an_approval_record(self):
        safe_examples = [
            "承認済みの素材だけを使用する。",
            "承認済の写真のみ採用する。",
            "画像が承認済の場合のみ公開する。",
            "画像は承認済ではない。",
            "承認済かどうかは要確認。",
            "承認済と誤認しない。",
        ]
        for line in safe_examples:
            with self.subTest(line=line):
                self.assertFalse(dp.is_unverified_approval_claim(line))
        self.assertTrue(dp.is_unverified_approval_claim(
            "| 写真利用許可 | 承認済 | 出典不明 |"
        ))
        self.assertTrue(dp.is_unverified_approval_claim(
            "| デザイン | 承認済み | 根拠未確認 |"
        ))

    def test_uploaded_draft_false_approval_regression(self):
        sample = (
            "| 生成画像の採用可否 | 承認済 | 【F001】 |\n"
            "| GitHub Pagesの静的公開 | 承認済 | 【F001】 |\n"
        )
        errs = dp.audit_claims(sample, self.case)
        self.assertTrue(any("承認記録" in e for e in errs))
        self.assertTrue(any("F001" in e for e in errs))

    def test_uploaded_draft_unsupported_cta_regression(self):
        sample = "| 売場の主CTA | 「今すぐ予約」ボタンを設置 | 未確認（要質問） |\n"
        errs = dp.audit_claims(sample, self.case)
        self.assertTrue(any("予約機能" in e for e in errs))

    def test_budget_table_sum_overrun(self):
        sample = (
            "| 実装 | A | 4時間 | 注記 |\n"
            "| 公開 | A | 2時間 | 注記 |\n"
            "| 画像 | B | 4時間 | 注記 |\n"
            "| 修正 | C | 1時間 | 注記 |\n"
            "| 引き渡し | C | 2時間 | 注記 |\n"
            "| その他 | C | 2時間 | 注記 |\n"
        )
        errs = dp.audit_claims(sample, self.case)
        self.assertTrue(any("15.0時間" in e for e in errs))

    def test_inconsistent_invented_paths(self):
        sample = "サブパス \x60/ao/\x60 と \x60/aogaro/\x60"
        errs = dp.audit_claims(sample, self.case)
        self.assertTrue(any("矛盾する公開パス" in e for e in errs))

    def test_invalid_image_permissions_regression(self):
        sample = "本案件では生成画像を許可する。\n"
        errs = dp.audit_claims(sample, self.case)
        self.assertTrue(any("生成画像" in e for e in errs))

    def test_ai_summary_is_not_quality_assessment(self):
        text = "\n".join("## " + t for t in dp.required_headers("requirements"))
        review = "## PM・運用審査\n構成を紹介。\n## Webデザイナー兼フロントエンド審査\n要約のみ。"
        errs = dp.audit_document("requirements", text, self.case, review)
        self.assertTrue(any("具体的な点数" in e for e in errs))
        self.assertTrue(any("減点" in e for e in errs))

    def test_copy_outline_is_truthful_and_complete(self):
        proposed = dp.demo_copy_outline_template(self.case)
        self.assertEqual([], dp.audit_claims(proposed, self.case))
        self.assertTrue(proposed.startswith("## セクション構成・コピー・NG表現"))
        self.assertIn("NG表現", proposed)
        self.assertIn("要件", proposed)
        self.assertIn("未確認", proposed)
        self.assertNotIn("承認済", proposed)

    def test_copy_outline_restores_without_touching_photo_ledger(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            paths = dp.case_paths(root)
            dp.save_json(paths["case"], self.case)
            dp.save_text(paths["requirements"], "previous draft")
            safe_photo = dp.demo_photo_ledger_template(self.case)
            dp.save_text(root / "requirements_section_04_2.md", safe_photo)
            for cid, titles in dp.CHAPTERS["requirements"]:
                if cid != "04":
                    content = "\n\n".join(
                        "## " + title + "\n\n" + "未確認情報は推測しない。人間へ確認を求める。" * 24
                        for title in titles
                    )
                    dp.save_text(root / ("requirements_chapter_" + cid + ".md"), content)
            with patch.object(dp, "model_reply") as ai:
                result = dp.restore_demo_copy_outline(root)
            ai.assert_not_called()
            self.assertEqual(6, result["chapters"])
            self.assertEqual("構造・出典検査済／AIレビュー未実施", result["status"])
            self.assertFalse(paths["approval"].exists())
            self.assertEqual(safe_photo, (root / "requirements_section_04_2.md").read_text())

    def test_deterministic_photo_ledger_has_no_unsupported_approval(self):
        template = dp.demo_photo_ledger_template(self.case)
        self.assertTrue(template.startswith("## 写真と素材台帳"))
        self.assertEqual([], dp.audit_claims(template, self.case))
        self.assertIn("未登録", template)
        self.assertIn("証跡", template)
        self.assertIn("使用不可", template)

    def test_photo_ledger_refuses_actual_assets(self):
        case = dict(self.case)
        case["assets"] = [{"id": "IMG001", "source": "human provided"}]
        with self.assertRaisesRegex(RuntimeError, "実素材"):
            dp.demo_photo_ledger_template(case)

    def test_photo_ledger_repairs_only_demo_without_model(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            p = dp.case_paths(root)
            dp.save_json(p["case"], self.case)
            dp.save_text(p["requirements"], "existing work that needs a section")
            for cid, titles in dp.CHAPTERS["requirements"]:
                if cid == "04":
                    title = titles[0]
                    text = "## " + title + "\n\n" + "素材は未確認であり人間の承認が必要です。" * 25
                    dp.save_text(root / "requirements_section_04_1.md", text)
                else:
                    body = "\n\n".join(
                        "## " + title + "\n\n" + "入力資料が不足するので未確認と記録する。" * 25
                        for title in titles
                    )
                    dp.save_text(root / ("requirements_chapter_" + cid + ".md"), body)
            with patch.object(dp, "model_reply") as model:
                result = dp.restore_demo_photo_ledger(root)
            model.assert_not_called()
            self.assertEqual(6, result["chapters"])
            self.assertEqual("構造・出典検査済／AIレビュー未実施", result["status"])
            self.assertFalse(result["automatic_approval"])
            self.assertFalse(p["approval"].exists())
            self.assertTrue((root / "requirements_section_04_2.md").exists())

    def test_salvage_only_never_uses_ai(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            p = dp.case_paths(root)
            dp.save_json(p["case"], self.case)
            dp.save_text(p["requirements"], "old incomplete draft")
            dp.save_json(p["req_quality"], {"status": "修正必要", "missing_or_unsafe": ["old"]})
            with patch.object(dp, "model_reply") as model:
                result = dp.repair_demo_requirements(root, allow_generation=False)
            model.assert_not_called()
            self.assertEqual("修正必要", result["status"])
            self.assertTrue(list(root.glob("requirements_qa_before_salvage_*.json")))

    def test_salvage_only_marks_ai_review_pending(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            p = dp.case_paths(root)
            dp.save_json(p["case"], self.case)
            dp.save_text(p["requirements"], "old draft")
            for chapter_id, titles in dp.CHAPTERS["requirements"]:
                chapter = "\n\n".join(
                    "## " + title + "\n\n" + ("未確認の事実を推測しない。まず担当者に質問する。" * 20)
                    for title in titles
                )
                dp.save_text(root / ("requirements_chapter_" + chapter_id + ".md"), chapter)
            with patch.object(dp, "model_reply") as model:
                result = dp.repair_demo_requirements(root, allow_generation=False)
            model.assert_not_called()
            self.assertEqual("構造・出典検査済／AIレビュー未実施", result["status"])
            self.assertTrue(result["review_pending"])
            self.assertFalse(p["approval"].exists())

    def test_repair_creates_backup_and_keeps_approval_absent(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            p = dp.case_paths(root)
            dp.save_json(p["case"], self.case)
            dp.save_text(p["requirements"], "original unapproved draft")
            dp.save_text(p["req_quality"], '{"status":"修正必要"}')
            dp.save_text(root / "requirements_chapter_01.md", "old chapter")
            with patch.object(dp, "draft_stage", return_value={"status": "修正必要"}) as mock:
                result = dp.repair_demo_requirements(root)
            self.assertEqual("修正必要", result["status"])
            self.assertEqual("original unapproved draft", (root / "backup_before_repair" / "requirements_draft.md").read_text())
            self.assertEqual("old chapter", (root / "backup_before_repair" / "requirements_chapter_01.md").read_text())
            self.assertFalse(p["approval"].exists())
            mock.assert_called_once()

    def test_repair_rejects_previous_human_approval(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            p = dp.case_paths(root)
            dp.save_json(p["case"], self.case)
            dp.save_text(p["requirements"], "do not overwrite")
            dp.save_json(p["approval"], {"reviewer": "human"})
            with self.assertRaisesRegex(RuntimeError, "承認記録"):
                dp.repair_demo_requirements(root)
            self.assertEqual("do not overwrite", p["requirements"].read_text())

    def test_old_passing_qa_is_rejected_on_audit(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            p = dp.case_paths(root)
            dp.save_json(p["case"], self.case)
            draft = (
                "## " + "\n\n## ".join(dp.required_headers("requirements")) +
                "\n| 生成画像の採用可否 | 承認済 | 【F001】 |\n"
            )
            dp.save_text(p["requirements"], draft)
            dp.save_json(p["req_quality"], {
                "status": "人間の承認待ち", "missing_or_unsafe": []
            })
            dp.save_text(root / "requirements_ai_reviews.md", "要約のみ")
            r = dp.audit_existing(root)
            self.assertEqual("修正必要", r["status"])
            self.assertEqual(draft, p["requirements"].read_text())
            self.assertTrue((root / "requirements_qa_previous.json").exists())
            self.assertTrue(dp.read_json(p["req_quality"])["missing_or_unsafe"])
            with patch("builtins.input", return_value="承認する"):
                with self.assertRaisesRegex(RuntimeError, "承認"):
                    dp.approve_requirements(root)

    def test_design_cannot_start_without_human_approval(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            dp.save_json(dp.case_paths(root)["case"], self.case)
            with self.assertRaisesRegex(RuntimeError, "人間の承認がありません"):
                dp.draft_stage("design", root)

    def test_changed_requirements_block_design(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = dp.case_paths(root)
            dp.save_json(path["case"], self.case)
            dp.save_text(path["requirements"], "original")
            dp.save_json(path["approval"], {
                "reviewer": "human", "approved_at": "2026-10-23",
                "approved_sha256": dp.sha256("original")})
            dp.save_text(path["requirements"], "changed")
            with self.assertRaisesRegex(RuntimeError, "再承認が必要"):
                dp.approved_req(root)

    def test_existing_chapters_resume_and_review_only(self):
        def fake_model(system, user, predict=1800):
            if "審査役：" in user:
                return "暫定点数：50/100。重大問題：事実・権利が未確認。減点箇所：根拠がない。" * 25
            # The generator now asks for each section's body separately.
            return "これは架空の案件です。確認済みの実店舗情報はありません。" + (
                "確定できない情報は未確認として質問に残し、"
                "動作やアクセシビリティは設計提案として扱います。" * 15
            )
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            dp.save_json(dp.case_paths(root)["case"], self.case)
            with patch.object(dp, "model_reply", side_effect=fake_model) as model:
                first = dp.draft_stage("requirements", root)
                self.assertEqual("人間の承認待ち", first["status"])
                self.assertEqual(6, first["chapters"])
                second = dp.draft_stage("requirements", root)
                self.assertEqual("人間の承認待ち", second["status"])
                self.assertEqual(16, model.call_count)  # 12 sections once + 2 reviews on each run
            self.assertFalse(dp.case_paths(root)["approval"].exists())
            self.assertFalse(dp.case_paths(root)["design"].exists())

    def test_can_record_human_approval_after_review(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            paths = dp.case_paths(root)
            dp.save_json(paths["case"], self.case)
            valid_draft = "人間が確認した架空仕様\n" + "\n".join("## " + h for h in dp.required_headers("requirements"))
            dp.save_text(paths["requirements"], valid_draft)
            dp.save_json(paths["req_quality"], {
                "status": "人間の承認待ち", "missing_or_unsafe": []})
            with patch("builtins.input", return_value="承認する"):
                dp.approve_requirements(root)
            self.assertEqual(valid_draft, dp.approved_req(root))

if __name__ == "__main__":
    unittest.main()
