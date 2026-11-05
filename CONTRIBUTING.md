# Contributing

1. Keep tenant-specific values as `REPLACE_WITH_*` placeholders.
2. Do not add live secrets, customer prompts, or real evidence.
3. Label generated evidence `SYNTHETIC` and `not_customer_evidence`.
4. Update [SOURCE-REGISTER.md](SOURCE-REGISTER.md) when an API, permission, or KQL column changes.
5. Add or update a unit test for behavior changes.
6. Run `python -m unittest discover -s tests -v`.
7. Do not claim an integration is production-ready unless a tenant test with reviewer approval is attached.
8. Do not copy code from external reference repositories. Write original examples.
9. Preserve the disclaimer that control mappings are not compliance certifications.

Pull requests that enable ARM deployment by default, or that fail open on Purview errors, will be rejected.
