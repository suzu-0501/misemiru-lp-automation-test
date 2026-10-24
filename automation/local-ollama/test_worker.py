"""Unit tests: no Google/Ollama network requests."""
import unittest
from worker import (
    INPUT_HEADERS, QUEUE_HEADERS, REVIEW_HEADERS, NO_MISSING, eligible_jobs,
    validate_grounding,
)

class GateTests(unittest.TestCase):
    def fixture(self):
        intake = [""] * 18
        intake[0] = "TEST-LP-001"
        intake[1] = "架空喫茶アオ"
        intake[8] = "確認済み"
        intake[9] = "確認済み"
        intake[15] = "架空データの根拠のみ"
        queue = [""] * 8
        queue[0] = "TEST-LP-001"
        queue[2] = "要件定義レビュー準備"
        queue[3] = NO_MISSING
        queue[4] = "架空のLP要件定義を作成"
        review = [""] * 10
        review[0] = "TEST-LP-001"
        review[5] = "未確認"
        review[8] = "不可"
        return [[INPUT_HEADERS, intake], [QUEUE_HEADERS, queue],
                [REVIEW_HEADERS, review]]

    def test_unapproved_consent_blocks(self):
        x = self.fixture()
        x[0][1][8] = "未確認"
        self.assertEqual(([], 1), eligible_jobs(x))

    def test_unapproved_image_rights_blocks(self):
        x = self.fixture()
        x[0][1][9] = "未確認"
        self.assertEqual(([], 1), eligible_jobs(x))

    def test_missing_information_blocks(self):
        x = self.fixture()
        x[1][1][3] = "予約リンク要確認"
        self.assertEqual(([], 1), eligible_jobs(x))

    def test_queue_not_ready_blocks(self):
        x = self.fixture()
        x[1][1][2] = "不足情報あり：要確認"
        self.assertEqual(([], 1), eligible_jobs(x))

    def test_existing_draft_skips(self):
        x = self.fixture()
        x[2][1][4] = "すでに生成済み"
        self.assertEqual(([], 0), eligible_jobs(x))

    def test_approved_case_is_eligible(self):
        x = self.fixture()
        jobs, blocked = eligible_jobs(x)
        self.assertEqual(0, blocked)
        self.assertEqual([(2,"TEST-LP-001","架空のLP要件定義を作成")], jobs)


class GroundingTests(unittest.TestCase):
    def test_reject_fake_sheet_verification(self):
        with self.assertRaisesRegex(RuntimeError, "出典未確認"):
            validate_grounding("所在地：東京都港区（シート確認済）", "架空喫茶アオ")

    def test_reject_unsupplied_business_hours(self):
        with self.assertRaisesRegex(RuntimeError, "入力に存在しない"):
            validate_grounding("営業時間：10:00〜22:00", "店舗名：架空喫茶アオ")

    def test_reject_unsupplied_seating(self):
        with self.assertRaisesRegex(RuntimeError, "入力に存在しない"):
            validate_grounding("定員：15名", "店舗名：架空喫茶アオ")

    def test_allow_unknowns_and_questions(self):
        validate_grounding(
            "所在地：未確認。営業時間：確認してください。CTAと写真利用権も質問します。",
            "架空喫茶アオ")

    def test_allow_exact_sourced_time_as_draft(self):
        validate_grounding("案内：10:00〜18:00（入力値、要確認）", "入力情報：10:00〜18:00")

if __name__ == "__main__":
    unittest.main()
