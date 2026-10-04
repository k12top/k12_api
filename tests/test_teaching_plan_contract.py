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
            "ListClassOfferings",
            "CreateClassOffering",
            "UpdateClassOffering",
            "PublishClassOffering",
            "ListAvailableClassOfferings",
            "EnrollClassOffering",
            "ListTeachingPlanTemplates",
            "CreateTeachingPlanTemplate",
            "CloneTeachingPlanTemplate",
            "GetTeachingPlanTemplate",
            "CreateTeachingPlanDraft",
            "SaveTeachingPlanDraft",
            "PublishTeachingPlanVersion",
            "ListSchedulingResources",
            "BatchApplyTeachingPlanToOfferings",
            "ListClassPlanAssignments",
            "GetClassPlanTimeline",
            "UpdateClassPlanAssignment",
            "PutClassPlanItemOverride",
            "DeleteClassPlanItemOverride",
            "PublishClassPlanAssignment",
            "GetMyCourseSchedule",
            "GetMyChapterSchedule",
            "GetMyLessonSchedule",
            "InitializeTeachingPlanLessons",
            "OpenLearningTask",
            "PutClassPlanLessonOverride",
            "DeleteClassPlanLessonOverride",
            "CompleteExternalLearningTask",
            "ReceiveOpenMAICProgressEvent",
            "ReceiveLiveProgressEvent",
            "ListClassOfferingMembers",
            "AddClassOfferingMember",
            "RemoveClassOfferingMember",
            "ListClassPlanLiveInstances",
            "PreviewOfferingLiveChanges",
            "ApplyOfferingLiveChanges",
            "SetLiveInstanceTeacherOverride",
            "ClearLiveInstanceTeacherOverride",
        }
        methods = set(re.findall(r"\brpc\s+(\w+)\s*\(", self.source))
        self.assertEqual(expected, methods)

    def test_public_live_series_fields_replace_standalone_course_fields(self):
        offering = re.search(r"(?s)message ClassOffering\s*\{(.*?)\n\}", self.source).group(1)
        self.assertIn("external_live_series_id", offering)
        self.assertIn("live_series_status", offering)

        instance = re.search(r"(?s)message ClassPlanLiveInstance\s*\{(.*?)\n\}", self.source).group(1)
        self.assertIn("external_live_session_id", instance)
        self.assertIn("sso_embed_url", instance)
        self.assertNotIn("external_live_course_id", instance)
        self.assertNotIn("classroom_url", instance)

        timeline = re.search(r"(?s)message ClassPlanTimelineItem\s*\{(.*?)\n\}", self.source).group(1)
        self.assertIn("external_live_series_id", timeline)
        self.assertIn("external_live_session_id", timeline)
        self.assertIn("sso_embed_url", timeline)

    def test_authenticated_external_completion_does_not_accept_learner_identity(self):
        request = re.search(r"(?s)message CompleteExternalLearningTaskRequest\s*\{(.*?)\n\}", self.source).group(1)
        for field in (
            "assignment_id",
            "plan_item_id",
            "provider",
            "event_id",
            "event_type",
            "occurred_at",
            "external_resource_id",
        ):
            self.assertIn(field, request)
        self.assertNotIn("casdoor", request)
        self.assertNotIn("user_id", request)
        self.assertIn('post: "/v1/learning/tasks/{plan_item_id}:complete-external"', self.source)

    def test_webhook_payloads_cover_openmaic_and_classin_contracts(self):
        openmaic = re.search(r"(?s)message OpenMAICShareWebhookEvent\s*\{(.*?)\n\}", self.source).group(1)
        for field in ("event_id", "event", "occurred_at", "share_token", "external_id"):
            self.assertIn(field, openmaic)

        classin = re.search(r"(?s)message ClassinLifecycleWebhookEvent\s*\{(.*?)\n\}", self.source).group(1)
        for field in ("event_id", "event", "occurred_at", "course_id", "session_id"):
            self.assertIn(field, classin)

    def test_student_schedule_is_resolved_by_course_and_casdoor_subject(self):
        self.assertRegex(self.source, r"(?s)message ClassOfferingMember\s*\{[^}]*casdoor_subject")
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
            "CompleteExternalLearningTask",
        }
        methods = set(re.findall(r"\brpc\s+(\w+)\s*\(", self.source))
        self.assertTrue(expected_methods.issubset(methods))
        self.assertRegex(
            self.source,
            r"(?s)message TeachingPlanItem\s*\{[^}]*chapter_id[^}]*live_duration_minutes",
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

    def test_lesson_contract_nests_items_and_preserves_legacy_fields(self):
        lesson = re.search(r"(?s)message TeachingPlanLesson\s*\{(.*?)\n\}", self.source)
        self.assertIsNotNone(lesson)
        lesson_source = lesson.group(1)
        for field in (
            "id",
            "title",
            "lesson_no",
            "sort_order",
            "source_chapter_id",
            "schedule_mode",
            "relative_day",
            "time_of_day_minutes",
            "absolute_unlock_at",
            "required",
            "repeated TeachingPlanItem items",
        ):
            self.assertIn(field, lesson_source)

        item = re.search(r"(?s)message TeachingPlanItem\s*\{(.*?)\n\}", self.source).group(1)
        self.assertRegex(item, r"int64 chapter_id\s*=\s*18\s*;")
        self.assertRegex(item, r"int64 plan_lesson_id\s*=\s*20\s*;")

        version = re.search(r"(?s)message TeachingPlanVersion\s*\{(.*?)\n\}", self.source).group(1)
        self.assertRegex(version, r"repeated TeachingPlanItem items\s*=\s*7\s*;")
        self.assertRegex(version, r"repeated TeachingPlanLesson lessons\s*=\s*12\s*;")

        save = re.search(r"(?s)message SaveTeachingPlanDraftRequest\s*\{(.*?)\n\}", self.source).group(1)
        self.assertRegex(save, r"repeated TeachingPlanItem items\s*=\s*3\s*;")
        self.assertRegex(save, r"repeated TeachingPlanLesson lessons\s*=\s*4\s*;")

    def test_lesson_routes_are_canonical_and_chapter_routes_remain_compatible(self):
        expected_routes = {
            'post: "/v1/admin/teaching-plan-template-versions/{version_id}/lessons:initialize"',
            'put: "/v1/admin/class-plan-assignments/{assignment_id}/lesson-overrides/{lesson_id}"',
            'delete: "/v1/admin/class-plan-assignments/{assignment_id}/lesson-overrides/{lesson_id}"',
            'get: "/v1/courses/{course_id}/lessons/{lesson_id}/schedule"',
            'post: "/v1/courses/{course_id}/lessons/{plan_lesson_id}/tasks/{plan_item_id}:open"',
            'post: "/v1/courses/{course_id}/chapters/{chapter_id}/tasks/{plan_item_id}:open"',
        }
        for route in expected_routes:
            self.assertIn(route, self.source)
        for message in (
            "LessonScheduleSummary",
            "ClassPlanLessonTimeline",
            "ClassPlanLessonOverride",
        ):
            self.assertIn(f"message {message}", self.source)

        values = {
            name: int(number)
            for name, number in re.findall(r"^\s*([A-Z][A-Z0-9_]+)\s*=\s*(\d+)\s*;", self.source, re.M)
        }
        self.assertEqual(1, values.get("STUDENT_LESSON_STATUS_LOCKED"))
        self.assertEqual(2, values.get("STUDENT_LESSON_STATUS_NOT_STARTED"))
        self.assertEqual(3, values.get("STUDENT_LESSON_STATUS_IN_PROGRESS"))
        self.assertEqual(4, values.get("STUDENT_LESSON_STATUS_COMPLETED"))


if __name__ == "__main__":
    unittest.main()
