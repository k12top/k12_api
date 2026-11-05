import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
PROTO = ROOT / "commerce" / "v1" / "commerce.proto"
EXAM_PROTO = ROOT / "exam" / "v1" / "exam.proto"


def message_body(source: str, name: str) -> str:
    match = re.search(rf"(?s)message {name}\s*\{{(.*?)\n\}}", source)
    return match.group(1) if match else ""


class CommerceContractTest(unittest.TestCase):
    def setUp(self):
        self.source = PROTO.read_text(encoding="utf-8")

    def test_checkout_trusts_server_price_and_site_context(self):
        body = message_body(self.source, "CreateCommerceCheckoutRequest")
        self.assertRegex(body, r"string offer_id\s*=\s*1\s*;")
        self.assertRegex(body, r"CommerceResourceType resource_type\s*=\s*2\s*;")
        self.assertRegex(body, r"string resource_id\s*=\s*3\s*;")
        self.assertNotRegex(body, r"\b(amount|price|site_id|organization_id)\b")

    def test_admin_mutations_require_audit_and_idempotency(self):
        for name in ("GrantResourceAccessRequest", "RevokeResourceAccessRequest", "ReplayCommerceFulfillmentRequest"):
            body = message_body(self.source, name)
            self.assertRegex(body, r"string reason\s*=\s*\d+\s*;", name)
            self.assertRegex(body, r"string idempotency_key\s*=\s*\d+\s*;", name)

    def test_resource_types_are_stable(self):
        self.assertIn("COMMERCE_RESOURCE_TYPE_CLASS_OFFERING_SEAT = 1;", self.source)
        self.assertIn("COMMERCE_RESOURCE_TYPE_EXAM_ATTEMPT = 2;", self.source)

    def test_exam_start_exposes_stable_commerce_state(self):
        exam = EXAM_PROTO.read_text(encoding="utf-8")
        self.assertIn("enum ExamCommerceState", exam)
        body = message_body(exam, "StartExamResponse")
        self.assertRegex(body, r"ExamCommerceState commerce_state\s*=\s*5\s*;")
        self.assertRegex(body, r"string commerce_reason\s*=\s*6\s*;")


if __name__ == "__main__":
    unittest.main()
