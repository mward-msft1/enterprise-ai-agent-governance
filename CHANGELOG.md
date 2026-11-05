# Changelog

## 0.1.1 — 2026-11-05

- Evidence hashes now use LF line endings, so the same SHA-256 matches on Windows, macOS, and Linux.
- CLI prints the workflow status and exits 1 when a prompt, response, or tool is denied.
- README includes macOS, Linux, and Windows run instructions.

## 0.1.0 — 2026-11-05

- Initial reference implementation.
- Offline synthetic workflow covering identity, authentication, Purview, Agent Framework boundary, MCP allowlist, audit, OpenTelemetry, and investigation bundle.
- Permissions matrix for the five named permissions, with delegated and application support distinguished.
- Nine prioritized detections, Sentinel ARM rules disabled by default, and Defender hunting queries.
- Tenant checklist, synthetic evidence, and evidence-replacement procedure.
- Local unit tests. No Microsoft tenant was contacted.

Known limitation: tenant integrations are not production-ready.
