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
        }
        methods = set(re.findall(r"\brpc\s+(\w+)\s*\(", self.source))
        self.assertEqual(expected, methods)

    def test_stable_enum_values(self):
        expected = {
            "PLAN_RESOURCE_TYPE_COURSE": 1,
            "PLAN_RESOURCE_TYPE_COURSEWARE": 2,
            "PLAN_RESOURCE_TYPE_EXAM": 3,
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


if __name__ == "__main__":
    unittest.main()
