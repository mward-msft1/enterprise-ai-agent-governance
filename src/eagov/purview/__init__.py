"""Microsoft Purview data security and governance adapters."""

from eagov.purview.content_activities import build_content_activity, record_content_activity
from eagov.purview.process_content import build_process_content_request, evaluate_content
from eagov.purview.protection_scopes import build_protection_scope_request, compute_protection_scopes

__all__ = [
    "build_content_activity",
    "build_process_content_request",
    "build_protection_scope_request",
    "compute_protection_scopes",
    "evaluate_content",
    "record_content_activity",
]
