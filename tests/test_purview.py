import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from eagov.models import AgentIdentity, PolicyDecision
from eagov.purview.content_activities import build_content_activity
from eagov.purview.process_content import interpret_process_content
from eagov.purview.protection_scopes import inline_activities


IDENTITY = AgentIdentity(
    agent_id="agent",
    blueprint_id="blueprint",
    application_id="app",
    display_name="Reference Agent",
    tenant_id="tenant",
)


class PurviewTests(unittest.TestCase):
    def test_inline_scope_is_detected(self):
        activities = inline_activities(
            [
                {"activities": "uploadText", "executionMode": "evaluateInline"},
                {"activities": "uploadFile", "executionMode": "evaluateOffline"},
            ]
        )
        self.assertEqual(activities, ["uploadText"])

    def test_restrict_access_block_denies(self):
        decision = interpret_process_content(
            "prompt",
            {
                "protectionScopeState": "modified",
                "policyActions": [
                    {
                        "@odata.type": "#microsoft.graph.restrictAccessAction",
                        "action": "restrictAccess",
                        "restrictionAction": "block",
                    }
                ],
                "processingErrors": [],
            },
            synthetic=True,
        )
        self.assertFalse(decision.allowed)

    def test_processing_errors_fail_closed(self):
        decision = interpret_process_content(
            "prompt",
            {
                "protectionScopeState": "notModified",
                "policyActions": [],
                "processingErrors": [{"message": "synthetic"}],
            },
            synthetic=True,
        )
        self.assertFalse(decision.allowed)

    def test_audit_body_omits_raw_text(self):
        body = build_content_activity(
            IDENTITY,
            "corr",
            "uploadText",
            "app",
            "0.1.0",
            PolicyDecision(
                stage="prompt",
                allowed=True,
                execution_mode="evaluateInline",
                protection_scope_state="notModified",
                synthetic=True,
            ),
        )
        serialized = str(body)
        self.assertNotIn("content", serialized.lower().split("contentmetadata")[0])
        self.assertNotIn("'data'", serialized)
        self.assertNotIn('"data"', serialized)


if __name__ == "__main__":
    unittest.main()
