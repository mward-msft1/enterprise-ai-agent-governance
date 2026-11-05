# Replace synthetic evidence

Files in `evidence/synthetic` and the rows in `TENANT-TEST-RESULTS.md` are synthetic. They are not customer results and they are not proof that a control operates in a tenant.

## 1. Execute authorized tenant tests

Use an authorized test tenant. Run one checklist item at a time from [checklists/tenant-configuration-checklist.csv](checklists/tenant-configuration-checklist.csv). Do not point tests at production users or production prompts.

## 2. Capture actual evidence

Save the portal export, redacted HTTP status, schema output, or policy decision. Store raw prompts outside the repository if they must be retained, and do not commit them.

## 3. Redact sensitive information

Remove access tokens, refresh tokens, client secrets, connection strings, API keys, employee personal data, customer content, and session cookies. Keep the identifier needed to verify the test, such as a correlation ID or application ID suffix.

## 4. Verify evidence provenance

Record who ran the test, the tenant ID suffix, the UTC time, and the command or portal path. Evidence from the authoring environment does not qualify.

## 5. Calculate SHA-256 hashes

Hash the redacted evidence file after redaction, not before. Published hashes in this repository are SHA-256 of the file with Windows CRLF converted to LF, so the same file matches on macOS, Linux, and Windows.

```bash
python -c "import hashlib,pathlib,sys; print(hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes().replace(b'\r\n', b'\n')).hexdigest())" evidence/tenant/TST-CFG-001.json
```

## 6. Store evidence securely

Put tenant evidence in the customer's approved store. If a redacted copy is committed, keep it under `evidence/tenant/` and do not mix it with `evidence/synthetic`.

## 7. Update test results

For each test, set actual result, evidence reference, tester, and status in `TENANT-TEST-RESULTS.csv`. Remove the synthetic wording only after the tenant artifact exists. Leave status as failed if the control did not pass.

## 8. Obtain reviewer approval

A second person reviews the evidence, hash, and pass criteria. Record the reviewer and date in the checklist and the test result. The tester cannot be the sole reviewer.

## 9. Document failures

If a control fails, record the status, the error, the residual risk, and the owner. Do not change the expected result to match the failure.

## 10. Retest remediated controls

After remediation, create a new evidence file. Do not overwrite the failed evidence. Update the hash, reviewer, and status. A retest is required before that control can be described as operating.

Synthetic hashes in `evidence/sample-evidence-manifest.json` validate the packaging procedure only.
