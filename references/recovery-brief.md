# Claude Account Recovery Brief

This is a sanitized reference brief for `claude-account-recovery`. It preserves
the operating constraints and phase structure of the recovery run that produced
this skill while removing personal names, organization names, host names, and
research-specific content.

## 0. Role, goal, and inputs

Act as a macOS digital-forensics, data-migration, and Claude Desktop/Code
recovery engineer. Recover the user's lawfully held data from an account that
has been deleted, disabled, or replaced. Produce an archive that is independent
of the old account and can be searched and resumed without reusing credentials
or bypassing an account restriction.

Inputs are supplied explicitly:

```text
EXPORT_DIR=<official Claude export directory>
LOCAL_RESEARCH_DIRS=<authorized local project directories>
RECOVERY_ROOT=<new output directory>
SSH_ALIAS=<optional authorized SSH host>
TARGET_ACCOUNT=<legitimate current account, if UI restoration is requested>
```

The export may contain:

- `manifest-*.json`
- `conversations-*.zip`
- `projects-*.zip`
- `memories-*.zip`
- `frames-*.zip`
- `light_metadata-*.zip`
- `feedback-*.zip`
- optionally a flat `conversations.json`

## 1. Non-negotiable safety constraints

1. Start read-only. Do not write to a Claude workspace, index, account,
   Keychain, or cloud service during inventory.
2. Back up before restoring. Quit Claude Desktop completely before any write.
   Copy source data; never move or clean it.
3. Require explicit approval for every write: `--apply`, `import-all`,
   `--to claude`, index changes, Cowork reconstruction, and cloud imports.
4. Never migrate authentication. Do not copy old OAuth, cookies, API keys,
   Keychain material, `.env`, broker tokens, or SSH private keys into the target
   account.
5. Never overwrite original data. Parsing and conversion write only to new
   directories.
6. Do not upload private research files, unpublished results, personal data, or
   recovery snapshots.
7. Audit every third-party repository before executing it. Record commit SHA,
   README claims, actual write paths, network behavior, and rollback.
8. Treat these as different outcomes: file backed up, local session readable,
   Desktop UI visible, same-context resumable, and cloud synchronized. Report
   each with evidence.

## 2. Recommended sources

Official documentation:

- <https://support.claude.com/en/articles/9450526-export-your-claude-data>
- <https://support.claude.com/en/articles/12123587-import-and-export-your-memory-from-claude>
- <https://code.claude.com/docs/en/desktop>
- <https://code.claude.com/docs/en/settings>
- <https://code.claude.com/docs/en/memory>
- <https://code.claude.com/docs/en/mcp>
- <https://support.claude.com/en/articles/15520349-use-claude-cowork-on-web-desktop-and-mobile>

Open-source tools:

- <https://github.com/onlyilkr/claude-migrate> — local Desktop Code index
  migration; inspect, isolate, plan, pilot, then apply.
- <https://github.com/PiniShv/AnthropicReader> — offline official-export reader.
- <https://github.com/XDUwt/claude-desktop-history> — Code/Cowork storage
  diagnostics; older storage model, so writes need isolation.
- <https://github.com/HeiGeAi/agent-history-rescue> — export-to-archive
  reference; can transform chats but does not recreate original Code state.
- <https://github.com/Dangelo123/claude-code-export-import> — cross-machine
  transcript/path-map analysis; cloud teleport requires old-account access.
- <https://github.com/ukogan/claude-migration-assistant> — Projects/Memory
  reconstruction methodology; outputs are approximations.
- <https://github.com/vitaliyhayda/claude-transplant> — do not use its cloud or
  Keychain paths.
- <https://github.com/selan-ai/claude-ai-export> — do not require an old login
  just to export already-available data.
- <https://github.com/ohmaseclaro/claude-acc> — forbidden for credential or
  account switching.

Exact revisions and compatibility findings are recorded in
`references/repo-audit.md`.

## 3. Phase P0 — authorization and environment

1. Record the macOS version, architecture, Claude Desktop version, and whether
   `CLAUDE_CONFIG_DIR` is set.
2. Confirm the target account's legitimate Claude Code entitlement.
3. Confirm which export, local project, and optional SSH sources are
   authorized.
4. Check free disk space and the expected backup size.
5. Do not request or print passwords, tokens, cookies, or private-key contents.

## 4. Phase P1 — inventory and immutable backup

Inventory:

- `~/.claude/`
- `~/.claude.json`
- `~/Library/Application Support/Claude/`
- `~/Library/Application Support/Code/User/`
- project-level `.claude/`, `CLAUDE.md`, `.mcp.json`
- Git repositories and worktrees
- official export ZIPs
- authorized remote `~/.claude/` and research directories

For each source record path, size, mtime, symlink state, and file count. Do not
execute discovered scripts.

Back up to a private `source-immutable/` directory with permissions `700`.
Generate SHA-256 manifests for files and hash symlink targets separately.

## 5. Phase P2 — parse, normalize, and deduplicate

1. Validate ZIP entry paths before extraction.
2. Parse conversation, message, branch, tool-call, attachment, project,
   artifact, frame, and memory records.
3. Preserve source name, file hash, session UUID, CLI session UUID, title,
   timestamps, order, branches, cwd, and transcript path.
4. Deduplicate by IDs and content hashes, not titles.
5. Build a separate searchable archive with source labels.

## 6. Phase P3 — research data and artifacts

Create a project state for each research project:

```text
projects/<name>/PROJECT_STATE.md
projects/<name>/SOURCE_LINKS.md
```

Record:

- objectives and assumptions;
- formulas and code locations;
- completed experiments and verified numbers;
- failed experiments and negative results;
- paper/manuscript status;
- open questions and next actions;
- source paths and hashes.

Extract Pages, decks, artifacts, attachments, and speaker notes. Never invent a
missing slide, result, or conclusion.

## 7. Phase P4 — Desktop Code restoration

1. Inspect `claude-code-sessions/<account>/<org>/local_*.json`.
2. Map `cliSessionId` to local or remote JSONL.
3. Skip records with no body; do not create empty shells.
4. Run `claude-migrate doctor` and `plan` in an isolated home.
5. Select one root session with a safe final state for a pilot.
6. Snapshot the target index, quit Desktop, install one index, and verify the
   title, history, tool calls, and input box.
7. After explicit approval, batch the remaining records and verify again.
8. Preserve the tool manifest and test `undo` or a target-file rollback.

Do not merge local web chats into a remote SSH workspace. Use separate local
and remote workspaces.

## 8. Phase P5 — Cowork and cloud boundaries

For old local Cowork, back up the index and body together:

```text
local_<sid>.json
local_<sid>/audit.jsonl
local_<sid>/outputs/
local_<sid>/uploads/
local_<sid>/.claude/
```

For a Cowork VM disk, copy the image, identify the format, expand only into
scratch space, verify the filesystem read-only, and search for missing UUIDs.

For post-2026-10-06 Cloud Cowork or Remote Control, use only an official,
currently authorized export/port/teleport flow. If access is unavailable,
produce a gap report and support-request draft. Do not use old credentials.

## 9. Phase P6 — Memory and configuration

Extract memory items and create a reviewable import draft. Remove stale
identity claims, personal data not needed for research, secrets, and
account-specific identifiers. Memory import is a separate cloud write; it does
not restore chat history.

Compare user-level and project-level `CLAUDE.md`, settings, Skills, Agents,
Commands, Hooks, plugins, MCP, IDE settings, and SSH aliases. Produce redacted
templates and a diff. Never restore `bypassPermissions` or old authorization
lists by default.

## 10. Phase P7 — verification and delivery

Required evidence:

- immutable-source checksum manifest;
- normalized session counts and JSON parse results;
- transcript path checks;
- Desktop UI opening checks;
- one same-context continuation test in the current account;
- SQLite integrity check;
- security scan with no secret values in the report;
- coverage report, gap report, final status, and rollback instructions.

Required final distinction:

```text
Local readable:       yes/no and evidence
Desktop UI visible:   yes/no and evidence
Resumable:            yes/no and evidence
Cloud synchronized:   verified / not verified
```

Never state that local JSONL/index recovery proves cloud synchronization.

## 11. Expected final package

```text
Claude-Recovery/
├── source-immutable/
├── conversations/
├── normalized/
├── sessions/
├── projects/
├── artifacts/
├── memory/
├── configs-redacted/
├── archive/
├── reports/
├── rollback/
├── tools/
└── Research-Workspace/
```

The package must be useful without the old account and must preserve original
evidence alongside derived summaries.
