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
            "ListMyClassOfferings",
            "ListTeachingPlanTemplates",
            "CreateTeachingPlanTemplate",
            "CreateTeachingPlanSetup",
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
            "ListClassOfferingMembers",
            "AddClassOfferingMember",
            "RemoveClassOfferingMember",
            "ListClassPlanLiveInstances",
            "RetryClassPlanLiveInstance",
            "PreviewOfferingLiveChanges",
            "ApplyOfferingLiveChanges",
            "SetLiveInstanceTeacherOverride",
            "ClearLiveInstanceTeacherOverride",
            "PreviewClassPlanSync",
            "ApplyClassPlanSync",
            "SaveTeachingPlanLesson",
            "PreviewTeachingPlanLessonSync",
            "ApplyTeachingPlanLessonSync",
        }
        methods = set(re.findall(r"\brpc\s+(\w+)\s*\(", self.source))
        self.assertEqual(expected, methods)

    def test_guided_teaching_plan_setup_contract_is_explicit(self):
        self.assertIn(
            "rpc CreateTeachingPlanSetup(CreateTeachingPlanSetupRequest) returns (TeachingPlanSetupResult)",
            self.source,
        )
        self.assertIn('post: "/v1/admin/teaching-plan-setups"', self.source)
        values = {
            name: int(number)
            for name, number in re.findall(r"^\s*([A-Z][A-Z0-9_]+)\s*=\s*(\d+)\s*;", self.source, re.M)
        }
        self.assertEqual(0, values.get("TEACHING_PLAN_SETUP_MODE_UNSPECIFIED"))
        self.assertEqual(1, values.get("TEACHING_PLAN_SETUP_MODE_OUTLINE_STANDARD"))
        self.assertEqual(2, values.get("TEACHING_PLAN_SETUP_MODE_OUTLINE_AI_ONLY"))
        self.assertEqual(3, values.get("TEACHING_PLAN_SETUP_MODE_OUTLINE_CUSTOM"))
        self.assertEqual(4, values.get("TEACHING_PLAN_SETUP_MODE_BLANK"))

        request = re.search(r"(?s)message CreateTeachingPlanSetupRequest\s*\{(.*?)\n\}", self.source).group(1)
        for expression in (
            r"string name\s*=\s*1\s*;",
            r"string description\s*=\s*2\s*;",
            r"int64 entry_course_id\s*=\s*3\s*;",
            r"TeachingPlanSetupMode mode\s*=\s*4\s*;",
            r"bool include_live\s*=\s*5\s*;",
            r"bool include_ai\s*=\s*6\s*;",
            r"int32 live_duration_minutes\s*=\s*7\s*;",
            r"int32 initial_lesson_count\s*=\s*8\s*;",
            r"repeated OutlineLessonGroup outline_lesson_groups\s*=\s*9\s*;",
        ):
            self.assertRegex(request, expression)

        result = re.search(r"(?s)message TeachingPlanSetupResult\s*\{(.*?)\n\}", self.source).group(1)
        for field in ("template", "version", "lesson_count", "live_task_count", "ai_task_count", "ready_for_class", "blocking_issues"):
            self.assertIn(field, result)

    def test_recurring_schedule_contract_preserves_presence_and_room_types(self):
        defaults = re.search(
            r"(?s)message TeachingPlanScheduleDefaults\s*\{(.*?)\n\}", self.source
        )
        self.assertIsNotNone(defaults)
        defaults_body = defaults.group(1)
        for expression in (
            r"string timezone\s*=\s*1\s*;",
            r"repeated int32 weekdays\s*=\s*2\s*;",
            r"string local_start_time\s*=\s*3\s*;",
            r"int32 live_duration_minutes\s*=\s*4\s*;",
            r"int32 live_room_type\s*=\s*5\s*;",
        ):
            self.assertRegex(defaults_body, expression)

        lesson = re.search(
            r"(?s)message TeachingPlanLesson\s*\{(.*?)\n\}", self.source
        ).group(1)
        for expression in (
            r"optional int32 schedule_weekday_override\s*=\s*12\s*;",
            r"optional string schedule_local_start_time_override\s*=\s*13\s*;",
            r"optional int32 live_duration_minutes_override\s*=\s*14\s*;",
            r"optional int32 live_room_type_override\s*=\s*15\s*;",
        ):
            self.assertRegex(lesson, expression)

        version = re.search(
            r"(?s)message TeachingPlanVersion\s*\{(.*?)\n\}", self.source
        ).group(1)
        self.assertRegex(
            version, r"TeachingPlanScheduleDefaults schedule_defaults\s*=\s*13\s*;"
        )
        setup = re.search(
            r"(?s)message CreateTeachingPlanSetupRequest\s*\{(.*?)\n\}", self.source
        ).group(1)
        self.assertRegex(
            setup, r"TeachingPlanScheduleDefaults schedule_defaults\s*=\s*10\s*;"
        )
        draft = re.search(
            r"(?s)message SaveTeachingPlanDraftRequest\s*\{(.*?)\n\}", self.source
        ).group(1)
        self.assertRegex(
            draft, r"TeachingPlanScheduleDefaults schedule_defaults\s*=\s*5\s*;"
        )

        self.assertIn("0=one-to-one", self.source)
        self.assertIn("4=small class (default)", self.source)
        self.assertIn("2=large class", self.source)
        self.assertIn("10=public class", self.source)

    def test_ai_playback_snapshots_and_outline_groups_preserve_existing_types(self):
        values = {
            name: int(number)
            for name, number in re.findall(
                r"^\s*([A-Z][A-Z0-9_]+)\s*=\s*(\d+)\s*;", self.source, re.M
            )
        }
        self.assertEqual(1, values.get("PLAN_RESOURCE_TYPE_COURSE"))
        self.assertEqual(5, values.get("PLAN_RESOURCE_TYPE_SECTION"))
        self.assertNotIn("PLAN_RESOURCE_TYPE_EXTERNAL_AI", values)

        item = re.search(
            r"(?s)message TeachingPlanItem\s*\{(.*?)\n\}", self.source
        ).group(1)
        self.assertRegex(item, r"string play_url\s*=\s*23\s*;")
        self.assertRegex(
            item, r"map<string, string> play_url_i18n\s*=\s*24\s*;"
        )

        node = re.search(
            r"(?s)message OutlineNodeRef\s*\{(.*?)\n\}", self.source
        ).group(1)
        self.assertRegex(node, r"int64 chapter_id\s*=\s*1\s*;")
        self.assertRegex(node, r"int64 section_id\s*=\s*2\s*;")

        group = re.search(
            r"(?s)message OutlineLessonGroup\s*\{(.*?)\n\}", self.source
        ).group(1)
        self.assertRegex(group, r"string title\s*=\s*1\s*;")
        self.assertRegex(group, r"repeated OutlineNodeRef nodes\s*=\s*2\s*;")

    def test_class_creation_returns_generated_schedule_and_accepts_idempotency_key(self):
        self.assertIn("rpc CreateClassOffering(CreateClassOfferingRequest) returns (CreateClassOfferingResult)", self.source)
        request = re.search(r"(?s)message CreateClassOfferingRequest\s*\{(.*?)\n\}", self.source).group(1)
        self.assertRegex(request, r"string request_id\s*=\s*15\s*;")
        result = re.search(r"(?s)message CreateClassOfferingResult\s*\{(.*?)\n\}", self.source).group(1)
        for field in ("offering", "assignment", "generated_lesson_count", "generated_task_count", "provisioning"):
            self.assertIn(field, result)

    def test_started_class_plan_sync_has_preview_and_revision_confirmation(self):
        self.assertIn("rpc PreviewClassPlanSync(PreviewClassPlanSyncRequest) returns (ClassPlanSyncPreview)", self.source)
        self.assertIn("rpc ApplyClassPlanSync(ApplyClassPlanSyncRequest) returns (ClassPlanAssignment)", self.source)
        self.assertIn('post: "/v1/admin/class-offerings/{offering_id}/plan-sync:preview"', self.source)
        self.assertIn('post: "/v1/admin/class-offerings/{offering_id}/plan-sync:apply"', self.source)
        preview = re.search(r"(?s)message ClassPlanSyncPreview\s*\{(.*?)\n\}", self.source).group(1)
        for field in ("added_count", "removed_count", "moved_count", "replaced_count", "protected_count", "revision"):
            self.assertIn(field, preview)
        apply = re.search(r"(?s)message ApplyClassPlanSyncRequest\s*\{(.*?)\n\}", self.source).group(1)
        self.assertRegex(apply, r"int64 expected_revision\s*=\s*3\s*;")

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

    def test_student_schedule_is_resolved_by_course_and_casdoor_subject(self):
        self.assertRegex(self.source, r"(?s)message ClassOfferingMember\s*\{[^}]*casdoor_subject")
        self.assertRegex(self.source, r"(?s)message TeachingPlanTemplate\s*\{[^}]*entry_course_id")
        self.assertIn('get: "/v1/courses/{course_id}/schedule"', self.source)

    def test_student_class_list_contract_is_offering_scoped(self):
        self.assertIn("rpc ListMyClassOfferings(ListMyClassOfferingsRequest) returns (ListMyClassOfferingsResponse)", self.source)
        self.assertIn('get: "/v1/user/class-offerings"', self.source)
        summary = re.search(r"(?s)message MyClassOfferingSummary\s*\{(.*?)\n\}", self.source).group(1)
        for field in (
            "offering",
            "course_id",
            "course_title",
            "course_cover_url",
            "assignment_id",
            "total_lesson_count",
            "completed_lesson_count",
            "next_lesson_id",
            "next_task_id",
            "next_task_title",
            "next_task_type",
            "next_task_unlock_at",
            "schedule_ready",
            "completed",
        ):
            self.assertIn(field, summary)

    def test_student_schedule_accepts_offering_context(self):
        for message_name in ("GetMyCourseScheduleRequest", "GetMyChapterScheduleRequest", "GetMyLessonScheduleRequest", "OpenLearningTaskRequest"):
            request = re.search(rf"(?s)message {message_name}\s*\{{(.*?)\n\}}", self.source).group(1)
            self.assertIn("offering_id", request, message_name)

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
        course = re.search(r"(?s)message CourseResource\s*\{(.*?)\n\}", self.source).group(1)
        for field in ("subject", "stage", "grade"):
            self.assertIn(field, course)

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
