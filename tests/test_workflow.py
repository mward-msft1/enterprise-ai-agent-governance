import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from eagov.config import load_config
from eagov.workflow import BLOCK_MARKER, RESPONSE_BLOCK_MARKER, GovernanceWorkflow


class WorkflowTests(unittest.TestCase):
    def test_offline_happy_path_records_every_stage(self):
        result = GovernanceWorkflow(load_config(mode="offline")).run(
            prompt="Summarize the public status page."
        )
        self.assertEqual(result.status, "allowed")
        self.assertFalse(result.production_ready)
        self.assertTrue(result.synthetic)
        for stage in [
            "agent_identity",
            "user_authentication",
            "agent365_inventory",
            "protection_scopes",
            "prompt_policy",
            "agent_framework",
            "tool_mcp",
            "response_policy",
            "audit",
            "otel_export",
            "defender_sentinel",
        ]:
            self.assertIn(stage, result.stages)
        self.assertEqual(result.telemetry["destination"], "in-memory")
        self.assertFalse(result.telemetry["agent365_exported"])
        self.assertIn("uploadText", result.audit["scopes"]["inline_activities"])
        self.assertFalse(result.investigation["executed_against_tenant"])

    def test_prompt_block_skips_model_and_tool(self):
        result = GovernanceWorkflow(load_config(mode="offline")).run(
            prompt=f"{BLOCK_MARKER} restricted request"
        )
        self.assertEqual(result.status, "denied_prompt")
        self.assertIsNone(result.framework)
        self.assertIsNone(result.tool)
        self.assertIn("audit", result.stages)
        self.assertNotIn("agent_framework", result.stages)

    def test_response_block_still_audits(self):
        result = GovernanceWorkflow(load_config(mode="offline")).run(
            prompt=f"status {RESPONSE_BLOCK_MARKER}"
        )
        self.assertEqual(result.status, "denied_response")
        self.assertIsNotNone(result.framework)
        self.assertFalse(result.response_decision["allowed"])
        self.assertIn("audit", result.stages)

    def test_disallowed_tool_is_not_executed(self):
        result = GovernanceWorkflow(load_config(mode="offline")).run(
            prompt="Summarize the public status page.",
            tool_name="shell_exec",
        )
        self.assertEqual(result.status, "denied_tool")
        self.assertFalse(result.tool["allowed"])
        self.assertIn("error", result.tool["call"])


if __name__ == "__main__":
    unittest.main()
