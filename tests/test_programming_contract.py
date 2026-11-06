import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
PROTO = ROOT / "programming" / "v1" / "programming.proto"


class ProgrammingContractTest(unittest.TestCase):
    def setUp(self):
        self.source = PROTO.read_text(encoding="utf-8")

    def message(self, name: str) -> str:
        match = re.search(rf"(?s)message {name}\s*\{{(.*?)\n\}}", self.source)
        self.assertIsNotNone(match, f"missing message {name}")
        return match.group(1)

    def test_student_workflow_has_stable_http_routes(self):
        expected = {
            "GetProgrammingAssignment": 'get: "/v1/programming/assignments/{assignment_id}"',
            "GetProgrammingWork": 'get: "/v1/programming/works/{work_id}"',
            "SaveProgrammingWork": 'put: "/v1/programming/works/{work_id}"',
            "CreateProgrammingRun": 'post: "/v1/programming/runs"',
            "GetProgrammingRun": 'get: "/v1/programming/runs/{run_id}"',
            "CreateProgrammingSubmission": 'post: "/v1/programming/submissions"',
            "ListProgrammingSubmissions": 'get: "/v1/programming/assignments/{assignment_id}/submissions"',
        }
        for rpc, route in expected.items():
            self.assertIn(f"rpc {rpc}", self.source)
            self.assertIn(route, self.source)

    def test_mutations_are_versioned_and_idempotent(self):
        save = self.message("SaveProgrammingWorkRequest")
        self.assertRegex(save, r"int64 expected_version\s*=\s*3\s*;")

        for name in (
            "CreateProgrammingRunRequest",
            "CreateProgrammingSubmissionRequest",
        ):
            body = self.message(name)
            self.assertRegex(body, r"string idempotency_key\s*=\s*\d+\s*;")

    def test_student_requests_do_not_accept_server_owned_fields(self):
        request_names = re.findall(r"message (\w+Request)\s*\{", self.source)
        self.assertGreater(len(request_names), 0)
        for name in request_names:
            body = self.message(name)
            for forbidden in ("user_id", "score", "hidden_input", "expected_output"):
                self.assertNotRegex(body, rf"\b{forbidden}\b", f"{name} exposes {forbidden}")

    def test_hidden_test_results_cannot_reveal_test_data(self):
        result = self.message("ProgrammingTestResult")
        self.assertRegex(result, r"bool is_hidden\s*=\s*2\s*;")
        self.assertRegex(result, r"double awarded_points\s*=\s*4\s*;")
        self.assertRegex(result, r"double possible_points\s*=\s*5\s*;")
        self.assertNotRegex(result, r"\b(hidden_input|expected_output)\b")

    def test_public_models_include_language_status_and_timestamps(self):
        for enum_name in (
            "ProgrammingLanguage",
            "ExecutionStatus",
            "SubmissionStatus",
        ):
            self.assertRegex(self.source, rf"enum {enum_name}\s*\{{")
        self.assertIn('import "google/protobuf/timestamp.proto";', self.source)

    def test_multi_file_project_is_additive_and_keeps_legacy_source_fields(self):
        file_message = self.message("ProgrammingFile")
        self.assertRegex(file_message, r"string path\s*=\s*1\s*;")
        self.assertRegex(file_message, r"string content\s*=\s*2\s*;")

        project = self.message("ProgrammingProject")
        self.assertRegex(project, r"repeated ProgrammingFile files\s*=\s*1\s*;")
        self.assertRegex(project, r"string entry_file\s*=\s*2\s*;")

        work = self.message("ProgrammingWorkContent")
        self.assertRegex(work, r"string source\s*=\s*2\s*;")
        self.assertRegex(work, r"ProgrammingProject project\s*=\s*5\s*;")

        run = self.message("CreateProgrammingRunRequest")
        self.assertRegex(run, r"string source\s*=\s*3\s*;")
        self.assertRegex(run, r"ProgrammingProject project\s*=\s*6\s*;")


if __name__ == "__main__":
    unittest.main()
