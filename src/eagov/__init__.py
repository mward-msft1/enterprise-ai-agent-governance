"""Enterprise AI agent governance reference implementation.

Offline synthetic mode is locally testable. Tenant mode builds authorized
Microsoft API calls and must be validated in a customer test tenant before
any production claim.
"""

__version__ = "0.1.0"
SYNTHETIC_CLASSIFICATION = "SYNTHETIC"
NOT_PRODUCTION_READY = (
    "Tenant integrations in this repository are reference adapters. "
    "They are not production-ready until the customer completes "
    "TENANT-TEST-RESULTS.md in an authorized test tenant."
)
