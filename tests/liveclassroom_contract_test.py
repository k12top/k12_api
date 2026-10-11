import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
PROTO = ROOT / "liveclassroom" / "v1" / "liveclassroom.proto"


def message_fields(source: str, message: str) -> dict[str, int]:
    match = re.search(rf"message\s+{message}\s*\{{(?P<body>.*?)\n\}}", source, re.S)
    if not match:
        return {}
    return {
        name: int(number)
        for name, number in re.findall(
            r"^\s*(?:[.\w]+)\s+(\w+)\s*=\s*(\d+)\s*;",
            match.group("body"),
            re.M,
        )
    }


class LiveClassroomContractTest(unittest.TestCase):
    def setUp(self):
        self.source = PROTO.read_text(encoding="utf-8")

    def test_lifecycle_enums_have_stable_values(self):
        values = {
            name: int(number)
            for name, number in re.findall(
                r"^\s*([A-Z][A-Z0-9_]+)\s*=\s*(\d+)\s*;", self.source, re.M
            )
        }
        expected = {
            "LIVE_ACCESS_MODE_UNSPECIFIED": 0,
            "LIVE_ACCESS_MODE_SCHEDULED": 1,
            "LIVE_ACCESS_MODE_LIVE": 2,
            "LIVE_ACCESS_MODE_PROCESSING": 3,
            "LIVE_ACCESS_MODE_PLAYBACK": 4,
            "LIVE_ACCESS_MODE_FINISHED": 5,
            "LIVE_TARGET_BEHAVIOR_UNSPECIFIED": 0,
            "LIVE_TARGET_BEHAVIOR_IFRAME": 1,
            "LIVE_TARGET_BEHAVIOR_NEW_TAB": 2,
        }
        for name, number in expected.items():
            self.assertEqual(number, values.get(name), name)

    def test_verify_response_preserves_old_fields_and_adds_target(self):
        self.assertEqual(
            {
                "allowed": 1,
                "role": 2,
                "course_info": 3,
                "classroom_url": 4,
                "reason": 5,
                "access_mode": 6,
                "target_url": 7,
                "target_behavior": 8,
                "playback_url": 9,
                "record_url": 10,
            },
            message_fields(self.source, "VerifyCourseAccessResponse"),
        )

    def test_course_info_exposes_lifecycle_timestamps(self):
        self.assertEqual(
            {
                "name": 1,
                "room_type": 2,
                "teacher_name": 3,
                "status": 4,
                "start_time": 5,
                "end_time": 6,
            },
            message_fields(self.source, "CourseInfo"),
        )


if __name__ == "__main__":
    unittest.main()
