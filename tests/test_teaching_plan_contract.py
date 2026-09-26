import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
PROTO = ROOT / "teachingplan" / "v1" / "teaching_plan.proto"


class TeachingPlanContractTest(unittest.TestCase):
    def setUp(self):
        self.source = PROTO.read_text(encoding="utf-8")

    def test_service_exposes_scheduling_workflow(self):
        expected = {
            "ListTeachingClasses",
            "CreateTeachingClass",
            "UpdateTeachingClass",
            "ListTeachingClassMembers",
            "AddTeachingClassMember",
            "RemoveTeachingClassMember",
            "ListTeachingPlanTemplates",
            "CreateTeachingPlanTemplate",
            "GetTeachingPlanTemplate",
            "CreateTeachingPlanDraft",
            "SaveTeachingPlanDraft",
            "PublishTeachingPlanVersion",
            "ListSchedulingResources",
            "BatchCreateClassPlanAssignments",
            "ListClassPlanAssignments",
            "GetClassPlanTimeline",
            "UpdateClassPlanAssignment",
            "PutClassPlanItemOverride",
            "DeleteClassPlanItemOverride",
            "PublishClassPlanAssignment",
            "GetMyCourseSchedule",
            "GetMyChapterSchedule",
            "OpenLearningTask",
            "ReceiveOpenMAICProgressEvent",
            "ReceiveLiveProgressEvent",
        }
        methods = set(re.findall(r"\brpc\s+(\w+)\s*\(", self.source))
        self.assertEqual(expected, methods)

    def test_student_schedule_is_resolved_by_course_and_casdoor_subject(self):
        self.assertRegex(self.source, r"(?s)message TeachingClassMember\s*\{[^}]*casdoor_subject")
        self.assertRegex(self.source, r"(?s)message TeachingPlanTemplate\s*\{[^}]*entry_course_id")
        self.assertIn('get: "/v1/courses/{course_id}/schedule"', self.source)

    def test_stable_enum_values(self):
        expected = {
            "PLAN_RESOURCE_TYPE_COURSE": 1,
            "PLAN_RESOURCE_TYPE_COURSEWARE": 2,
            "PLAN_RESOURCE_TYPE_EXAM": 3,
            "PLAN_RESOURCE_TYPE_LIVE": 4,
            "TEACHING_ROLE_LESSON": 1,
            "TEACHING_ROLE_IN_CLASS_PRACTICE": 2,
            "TEACHING_ROLE_HOMEWORK": 3,
            "TEACHING_ROLE_ASSESSMENT": 4,
            "SCHEDULE_MODE_RELATIVE": 1,
            "SCHEDULE_MODE_ABSOLUTE": 2,
        }
        values = {
            name: int(number)
            for name, number in re.findall(r"^\s*([A-Z][A-Z0-9_]+)\s*=\s*(\d+)\s*;", self.source, re.M)
        }
        for name, number in expected.items():
            self.assertEqual(number, values.get(name), name)

    def test_chapter_player_contract(self):
        expected_methods = {
            "GetMyChapterSchedule",
            "OpenLearningTask",
            "ReceiveLiveProgressEvent",
        }
        methods = set(re.findall(r"\brpc\s+(\w+)\s*\(", self.source))
        self.assertTrue(expected_methods.issubset(methods))
        self.assertRegex(
            self.source,
            r"(?s)message TeachingPlanItem\s*\{[^}]*chapter_id[^}]*live_course_id",
        )
        self.assertRegex(
            self.source,
            r"(?s)message ClassPlanTimelineItem\s*\{[^}]*progress_status[^}]*presentation_status[^}]*launch_mode",
        )
        self.assertIn("message ChapterScheduleSummary", self.source)

    def test_scheduling_resources_expose_course_chapters(self):
        self.assertRegex(
            self.source,
            r"(?s)message CoursewareResource\s*\{[^}]*chapter_id",
        )
        self.assertRegex(
            self.source,
            r"(?s)message CourseResource\s*\{[^}]*repeated ChapterResource chapters",
        )

    def test_launch_and_progress_enums_are_explicit(self):
        expected = {
            "TASK_PROGRESS_STATUS_NOT_STARTED": 1,
            "TASK_PROGRESS_STATUS_IN_PROGRESS": 2,
            "TASK_PROGRESS_STATUS_COMPLETED": 3,
            "LAUNCH_MODE_IFRAME": 1,
            "LAUNCH_MODE_NEW_TAB": 2,
        }
        values = {
            name: int(number)
            for name, number in re.findall(r"^\s*([A-Z][A-Z0-9_]+)\s*=\s*(\d+)\s*;", self.source, re.M)
        }
        for name, number in expected.items():
            self.assertEqual(number, values.get(name), name)


if __name__ == "__main__":
    unittest.main()
