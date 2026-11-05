# Security

## Reporting

Report vulnerabilities privately to the repository maintainers. Do not include live tokens, customer prompts, or tenant evidence in a public issue.

## Design choices

- Secrets use `REPLACE_WITH_*` placeholders. Do not commit `.env`, client secrets, or connection strings.
- Tenant network calls are opt-in and fail if placeholders remain.
- Policy evaluation fails closed on processing errors and restrict-access actions.
- The MCP gateway denies tools that are not allowlisted.
- Audit recording omits raw prompt and response text.
- Analytics-rule deployment is off by default, and each rule is disabled.
- Azure resource deployment is off by default because the resources are billable.

## Scanning

`.github/workflows/security-scan.yml` runs a secret-pattern scan and a dependency manifest check. It does not replace GitHub secret scanning, Dependabot, or a tenant security review.

## Out of scope

This repository does not disable customer security controls, evade detection, or access a tenant without authorization.
