# Reference Instance: Claude Desktop Research Recovery

This file records the concrete recovery case that produced the skill. It is
evidence for reproducibility, not a claim about every Claude account.

## Environment

- macOS 26.5.2, arm64
- Claude Desktop `2.42304.2`
- Claude Code CLI was present locally but was not the migration target
- Official export contained six ZIP classes:
  `conversations`, `projects`, `memories`, `frames`, `light_metadata`,
  `feedback`
- A remote research host SSH host was authorized for read-only session and index checks
- The new account had legitimate Claude Code access after upgrade

No old-account OAuth, cookie, Keychain, API key, or SSH private key was copied
into the recovery pack.

## Outcome

### Desktop Code

- Old indexes found: 18
- Indexes with recoverable bodies: 15
- Installed into the new account: 15
- UI readable after restore: 15/15
- Active and resumable after unarchive: 15/15
- Indexes with only metadata/post-turn summaries: 3
- Empty-shell sessions fabricated: 0

The three missing bodies were not replaced by summaries. Their downstream
artifacts were archived separately as research evidence.

### Remote and local workspaces

- Real SSH/Code sessions: 100
- Remote transcript paths checked: 100
- Missing remote paths: 0
- Old Desktop Code sessions included in the remote workspace: 15
- Local `Research-Workspace` sessions: 88
- Active local sessions: 62
- Archived personal-life sessions: 26

The two sidebar groups were intentionally kept separate:

- `Research-Workspace`
- `workspace · REMOTE`

This prevents a local web-chat transcript from being mistaken for an SSH
session and keeps the real execution boundary.

### Web export

- Conversations: 119
- Messages: 2,286
- Date range: 2026-03-10 to 2026-10-14
- Conversations with recoverable human/assistant body: 87
- Textless conversations: 32
- Personal-life conversations archived by default: 26

The 87 bodies were converted into Code-compatible local sessions. The 32
textless conversations were retained as index/export evidence only.

### Projects, artifacts, and memory

- Official Projects: 3
- Projects archived offline: 3
- Projects recreated in the new cloud account: 0
- Artifact/Page objects: 8
- Artifact/Page objects archived: 8
- Deck versions complete: 25/26
- Deck pages with text and speaker notes: 506
- Memory aggregate: 1
- Memory item files: 13
- Memory imported into the new account: 0
- Old Skills found: 122
- Broken Skills: 0

### Search archive

- SQLite sessions: 435
- Messages: 23,760
- Documents: 236
- `PRAGMA integrity_check`: `ok`
- Sources preserved separately: Desktop Code, web export, remote-host CLI,
  SDK/autoresearch, subagents, artifacts, project evidence, reports

### Verification

- All 188 index records parsed with 0 JSON errors at final validation
- Security audit: 5,641 files scanned, 0 secret-pattern candidates,
  permissions OK
- Main manifest: 5,686 files checked, 0 failed
- Immutable snapshot: 2,709 entries checked, 0 failed after symlink-aware
  verification
- UI pilot: a research-writing session loaded its full history, and a follow-up
  message was accepted by the new account.
- Remote pilot: an environment-preparation session loaded remote history, and
  a follow-up message was accepted by the new account.
- Cloud synchronization: not verified and not claimed

## Reusable tool stack

### Built-in macOS tools

`find`, `ditto`, `cp -p`, `shasum`, `unzip`, `sqlite3`, `ssh`, `readlink`,
`rg`, `git`, `file`, and `xxd`.

### Recovery-pack helpers

The reference pack included these task-specific Python/Go/shell helpers:

- `audit_config_state.py`
- `audit_recovery_security.py`
- `audit_textless_webchats.py`
- `build_conversation_index.py`
- `build_delivery_manifest.py`
- `build_filtered_web_import.py`
- `build_research_workspace.py`
- `build_search_index.py`
- `consolidate_web_chats.py`
- `create_sensitive_vault.sh`
- `export_deck_text.py`
- `extract_asif_sparse.py`
- `fix_derived_filenames.py`
- `fix_memory_filenames.py`
- `import_uts_sessions.py`
- `import_web_chats_as_code.py`
- `normalize_claude_jsonl.py`
- `promote_workspace_sources.py`
- `redact_derived_secrets.py`
- `repair_redaction_corruption.py`
- `snapshot_local_transcripts.py`
- `test_unarchive_sandbox.py`
- `triage_web_chats.py`
- `verify_client_sessions.py`

The names are not a required implementation. The reusable logic is the
separation of raw evidence, normalized records, search index, local workspace,
and reversible client-index changes.

## External repositories and exact revisions

| Repository | Revision | Decision |
|---|---|---|
| `onlyilkr/claude-migrate` | `8a50250df9bc78cd8e5815c6162f5bb163930bcc` | Used for local Code index migration; isolated pilot then batch |
| `PiniShv/AnthropicReader` | `c261d19a42f9f449b65ca6863e5c56eeff46cfbb` | Local-only export reader |
| `XDUwt/claude-desktop-history` | `03b435348e68d472d578a5086903d557e969104a` | Read-only/reference; Cowork writes need isolated testing |
| `HeiGeAi/agent-history-rescue` | `8685238ea180c7fad4091d8cc6ec2f388a27baaa` | Read-only archive and converter reference |
| `Dangelo123/claude-code-export-import` | `9cec2b21a5c8ad9c84ca596da05d26a1333babd3` | Cross-machine analysis reference; cloud export disabled |
| `ukogan/claude-migration-assistant` | `42feb750522a4ee56ddc306c70d19d61c3fd2990` | Method reference only |
| `vitaliyhayda/claude-transplant` | `c24ea1c2cc973fe4a40f0a5501ca43828b28ff48` | Not used; cloud/Keychain path forbidden |
| `selan-ai/claude-ai-export` | `d6828c9919658b24a2003c1755b4b12ab3288f2a` | Not used; requires old login |
| `ohmaseclaro/claude-acc` | `eea0659eff2f62fe376ca9a4570dccae37ad0d63` | Forbidden; credential/account switching |

## Non-negotiable conclusions from this case

1. A local index is not a transcript.
2. A transcript cache is not a cloud copy.
3. A UI reply proves “can continue,” not “cloud synced.”
4. Web Chat, Desktop Code, Cowork, and Remote Control are different stores.
5. Converting web chats is a new local representation, not original Code state.
6. Empty sessions must not be created to improve a coverage number.
7. A desktop upgrade may rewrite index bytes; verify semantic fields and body
   reachability.
8. The correct side-by-side presentation is two workspaces, not one fake SSH
   workspace.
