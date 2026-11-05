import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from eagov.auth.graph_auth import ClientCredentialsTokenProvider, validate_permission_grant
from eagov.config import find_placeholders, load_config
from eagov.errors import ConfigurationError, TenantNotValidated
from eagov.identity.entra import load_matrix, validate_entra_configuration


class ConfigTests(unittest.TestCase):
    def test_template_placeholders_block_tenant_mode(self):
        config = load_config(mode="tenant")
        self.assertTrue(config.placeholders)
        with self.assertRaises(ConfigurationError):
            config.require_tenant_ready()

    def test_placeholder_finder(self):
        found = find_placeholders({"tenant": {"id": "REPLACE_WITH_TENANT_ID"}, "ok": "value"})
        self.assertEqual(found, ["tenant.id"])

    def test_client_credentials_request_is_not_executed_by_default(self):
        provider = ClientCredentialsTokenProvider("tenant", "client", "secret", execute=False)
        built = provider.build_request()
        self.assertIn("oauth2/v2.0/token", built["request"]["url"])
        self.assertNotIn("secret", built["request"]["body_fields"])
        with self.assertRaises(TenantNotValidated):
            provider()

    def test_matrix_distinguishes_delegated_and_application(self):
        matrix = load_matrix()
        by_name = {item["name"]: item for item in matrix["permissions"]}
        self.assertTrue(by_name["ContentActivity.Write"]["delegated"]["supported"])
        self.assertTrue(by_name["ContentActivity.Write"]["application"]["supported"])
        self.assertFalse(by_name["Agent365.Observability.OtelWrite"]["application"]["supported"])
        self.assertTrue(by_name["Agent365.Observability.OtelWrite"]["delegated"]["supported"])
        grant = validate_permission_grant(
            {
                "permission": "Content.Process.User",
                "delegated": ["Content.Process.User"],
                "application": ["Content.Process.User"],
            },
            ["Content.Process.User"],
            [],
        )
        self.assertTrue(grant["delegated_satisfied"])
        self.assertFalse(grant["application_satisfied"])

    def test_empty_grants_are_reported(self):
        report = validate_entra_configuration(load_config(mode="offline"))
        self.assertFalse(report["user_workflow_delegated_ready"])


if __name__ == "__main__":
    unittest.main()
