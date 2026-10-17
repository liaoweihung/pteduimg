# Review contract v1

## Capability evidence — checked 2026-10-18 (Asia/Taipei)

Local `C:\Users\liaow\AppData\Local\agy\bin\agy.exe --version` returned 1.4.0.
Only `--help`, `help`, and `--version` were run in this phase; no model was invoked.
Local help lists `--print`, `--output-format json`, `--print-timeout`, `--sandbox`,
`--mode`, `--agent`, `--project`, `--add-dir`, and `--disable-slash-commands`.
It exposes no all-tools-off switch, per-run permissions file, or cwd flag.

Official references actually read:

- [Headless mode](https://www.antigravity.google/docs/cli/headless/): print mode and JSON
  envelopes; denied approvals can still yield exit 0, and workspace file access can be allowed.
- [CLI commands/settings](https://www.antigravity.google/docs/cli/reference/): strict permission
  preset still excludes read tools from prompting; it is not a no-tools policy.
- [Agent permissions](https://www.antigravity.google/docs/permissions/): global settings support
  deny/ask/allow and action-wide wildcards for file, command, URL and MCP namespaces.
- [CLI features](https://www.antigravity.google/docs/cli/features): sandbox concerns local agent
  process containment, not removing every model tool.

These are current rolling documents, not a version-pinned 1.4.0 guarantee. Local help says
print timeout defaults to 0, whereas the current web guide says five minutes. Future transport
must set both CLI timeout and a host-enforced deadline explicitly.

The host can set `ProcessStartInfo.WorkingDirectory`; that is process cwd control, not proof of
no project discovery, parent rules, global skills, hooks, plugins, MCP or history loading.
`--project` selects a project; `--add-dir` adds access. Neither provides isolation.
Plan mode, slash disabling and an empty cwd are insufficient security boundaries.
No settings or credential files were inspected. Global deny settings were not changed.
Result: ISOLATION_UNVERIFIED. No live test or escalation was requested in this phase.

## Bounded input

`invoke_review.ps1 -PacketJson $json -Mode Validate|Simulate|Live`
accepts explicit text JSON only; no file paths, repository crawling or arbitrary extra arguments.
PowerShell 7 is required. Packet maximum: 24000 UTF-8 bytes, 1–8 unique page IDs, 0–12 sources.
Only these fields are accepted; all are required:

```json
{
  "page_ids": ["synthetic_example"],
  "audience": "合成測試讀者",
  "text": "合成文字：請先閱讀操作說明。",
  "previous_text": "",
  "sources": [{"title":"合成來源", "url":"https://example.org/source", "excerpt":"合成摘錄"}]
}
```

Empty sources is allowed for synthetic/nonmedical review, but must be disclosed as insufficient
for medical verification. URLs are labels, never fetched by the reviewer. Codex selects necessary
content and removes personal/secret data before invocation; size/schema checks cannot detect all secrets.

Canonicalization orders keys, sorts page IDs and sources, normalizes CRLF/CR to LF and Unicode to
NFC, and preserves other whitespace. `text_sha256` hashes canonical packet UTF-8 bytes.
`review_key` additionally binds prompt text and parser script hash (contract/implementation version).
Changing content, audience, scope, source excerpts or review instructions invalidates reuse.
Deduplication uses only explicitly supplied `-PreviousResultJson` successful, validated results
with matching keys and matching simulation provenance. Failure/incomplete/blocked results never cache.
The caller must retain prior results in an authorized record; no hidden disk cache is created.
This is sequential reuse, not a cross-process lock or cryptographic signature of model provenance.

## Review prompt and response

The generated prompt tells Gemini to use no tools, Git or files and treats the packet as untrusted
quoted data. This is defense in depth, not isolation. Return a plain JSON string in CLI `response`:

```json
{
  "summary":"繁體中文摘要",
  "findings":[{
    "page_id":"synthetic_example",
    "quote":"請先閱讀操作說明",
    "severity":"medium",
    "issue":"繁體中文問題",
    "recommendation":"繁體中文建議",
    "source_urls":[],
    "needs_verification":true
  }],
  "limitations":["僅依提供文字，未自行查閱來源"]
}
```

Findings may be empty. Severity is low/medium/high. Quotes must occur in submitted text or
previous_text, page IDs must be in scope, and cited URLs must come from supplied sources.
All keys/types are checked; markdown-wrapped, missing, malformed or out-of-scope output fails closed.
The parser cannot establish language quality or medical correctness: Codex checks these explicitly.

Outer CLI validation requires exit 0, case-exact SUCCESS, nonempty response, finite nonnegative
numeric duration_seconds. Unknown model remains null. Raw stderr, error messages, usage,
conversation IDs and unexpected envelope fields are not echoed or persisted.

## Execution/result contract

Modes: Validate builds packet/key/prompt locally; Simulate uses built-in synthetic fixtures;
Live always returns BLOCKED / ISOLATION_UNVERIFIED and cannot start agy in this version.
There is deliberately no override switch. Future transport must use the fixed absolute agy path,
argument arrays (never shell interpolation), `--print` and `--output-format json`, an external
deadline, separate stdout/stderr, closed stdin, no continuation and no inherited repository cwd.
Formal sandbox approval belongs to Codex, never this script. Do not auto-retry failed calls.

Output is one JSON object: state, reason, simulated, model_called, text_sha256, review_key,
duration_seconds, review, checked_at and contract_version. State is VALIDATED, COMPLETED,
REUSED, FAILED, TIMEOUT or BLOCKED. COMPLETED/REUSED in simulation is always labelled simulated;
model_called is false throughout phase one. Failure uses sanitized reason codes, not raw CLI text.
Script exits 0 for VALIDATED/COMPLETED/REUSED, 2 for blocked/failure, 3 for timeout.

Codex reports actual call status separately from content findings and human signoff. Never put AI
opinion in medical references, clear needsMedicalReview, or label a page pharmacist_reviewed.
No report file or management edit is automatic. Record failures in chat unless evidence writing is
within the current authorization. No medical data or project management files change in phase one.

## Phase two acceptance gaps

- Verify version-specific, session-scoped complete tool denial without modifying global settings.
- Verify no implicit repository/global context, hooks, plugins, MCP or history enters the request.
- Verify isolated cwd plus Windows process-tree deadline/cleanup for the real CLI backend.
- Under formal approval, test synthetic input and malicious tool requests; then explicitly authorize
  real review and SOP integration. Prior successful arithmetic answers do not prove containment.
