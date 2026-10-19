# Claude Account Recovery Runbook

This is the expanded execution guide for `claude-account-recovery`. Use
placeholders until the user supplies paths. Never infer an account, host, or
credential from a previous case.

## 0. Freeze the operating brief

Record these values before touching data:

```text
RECOVERY_ROOT=~/Documents/Claude-Recovery
EXPORT_DIR=<user-authorized official export directory>
DESKTOP_DATA=~/Library/Application Support/Claude
CLAUDE_HOME=~/.claude
SSH_ALIAS=<optional user-authorized SSH host>
NEW_ACCOUNT_INDEX=<target Claude Desktop Code index directory>
```

Confirm:

- which account is being recovered;
- whether the target account has legitimate Claude Code access;
- which research directories and SSH hosts are authorized;
- whether writes to the live Desktop index are allowed;
- whether the user wants a local-only archive or a resumable UI restore.

Do not accept a password. If an SSH private key is named by the user, use it
only for the authorized host and only for read-only inspection until a later
write approval.

## 1. Read-only inventory

### 1.1 Mac sources

Inventory, but do not print file contents:

- `~/.claude/`
- `~/.claude.json`
- `~/Library/Application Support/Claude/`
- `~/Library/Application Support/Code/User/`
- project-level `.claude/`, `CLAUDE.md`, `.mcp.json`
- Git repositories and worktrees associated with research projects
- potential `CLAUDE_CONFIG_DIR`

Useful non-destructive commands:

```bash
find "$CLAUDE_HOME" -maxdepth 4 -type f -print 2>/dev/null | sort
find "$DESKTOP_DATA" -maxdepth 6 -type f -print 2>/dev/null | sort
rg --files "$CLAUDE_HOME" "$DESKTOP_DATA" 2>/dev/null | wc -l
du -sh "$CLAUDE_HOME" "$DESKTOP_DATA" 2>/dev/null
```

Record counts, sizes, timestamps, symlinks, broken symlinks, and whether a
directory is user-owned or project-owned. Do not run Spotlight or file indexing
commands that write application state.

### 1.2 Official export

For each ZIP:

```bash
shasum -a 256 "$EXPORT_DIR"/*.zip
unzip -l "$EXPORT_DIR/conversations-000.zip"
unzip -l "$EXPORT_DIR/projects-000.zip"
unzip -l "$EXPORT_DIR/memories-000.zip"
unzip -l "$EXPORT_DIR/frames-000.zip"
unzip -l "$EXPORT_DIR/light_metadata-000.zip"
unzip -l "$EXPORT_DIR/feedback-000.zip"
```

Reject or quarantine entries with `../`, absolute paths, device files, or
unexpected symlinks. Extract only into a sandbox directory.

Validate `conversations.json` structurally:

```bash
python3 - "$EXPORT_DIR/conversations.json" <<'PY'
import json, sys
p = sys.argv[1]
data = json.load(open(p, encoding="utf-8"))
print(type(data).__name__)
print(len(data) if isinstance(data, list) else sorted(data))
PY
```

Record the number of conversations, messages, projects, artifacts, memories,
attachments, and missing attachment references.

### 1.3 SSH sources

Only if the user explicitly authorizes the host:

```bash
ssh "$SSH_ALIAS" 'find ~/.claude/projects -maxdepth 3 -type f -name "*.jsonl" -printf "%p\t%s\n" 2>/dev/null | head'
ssh "$SSH_ALIAS" 'find ~/.claude -maxdepth 3 -type f \( -name "*.json" -o -name "*.jsonl" \) -printf "%p\t%s\n" 2>/dev/null | head'
```

Do not copy multi-GB result directories. Copy only the authorized session
metadata and transcripts needed to prove recoverability. Keep remote session
data separate from local data.

## 2. Immutable backup before any transformation

Create a private, timestamped snapshot:

```bash
STAMP=$(date +%Y%m%dT%H%M%S)
mkdir -p "$RECOVERY_ROOT/source-immutable"
umask 077
ditto "$CLAUDE_HOME" "$RECOVERY_ROOT/source-immutable/claude-home-$STAMP"
ditto "$DESKTOP_DATA" "$RECOVERY_ROOT/source-immutable/claude-desktop-$STAMP"
mkdir -p "$RECOVERY_ROOT/source-immutable/export-$STAMP"
cp -p "$EXPORT_DIR"/*.zip "$RECOVERY_ROOT/source-immutable/export-$STAMP/"
```

If `ditto` is unavailable, use `cp -pR` and verify the result. Do not use
`mv`, `rsync --delete`, or any cleanup command.

Generate a hashes file:

```bash
find "$RECOVERY_ROOT/source-immutable" -type f -print0 \
  | xargs -0 shasum -a 256 > "$RECOVERY_ROOT/reports/SHA256SUMS-source-immutable.txt"
```

For symlinks, verify the link target and target file. A plain `shasum -c`
reports a symlink as unreadable; verify the target with Python or `readlink`
and record the rule in the report.

Protect credentials:

```bash
chmod 700 "$RECOVERY_ROOT" "$RECOVERY_ROOT/source-immutable"
find "$RECOVERY_ROOT/source-immutable" -type d -exec chmod 700 {} +
find "$RECOVERY_ROOT/source-immutable" -type f -exec chmod 600 {} +
```

Do not upload `source-immutable/live-*`, `metadata/private/`, Keychain
material, OAuth files, cookies, `.env`, or SSH private keys.

## 3. Parse, normalize, and deduplicate

Create separate normalized namespaces:

```text
normalized/desktop-code/
normalized/web-export/
normalized/uts-ssh/
normalized/cowork/
normalized/artifacts/
```

For every normalized record keep:

- source name and source file hash;
- original conversation/session UUID;
- CLI session UUID when present;
- title and title source;
- created/updated timestamps;
- message role and original order;
- branches and parent UUIDs;
- tool calls and tool results;
- working directory and SSH alias (redact in public reports);
- attachment UUID or path, and whether the binary actually exists.

Do not deduplicate by title. Use UUIDs first, then content hashes. Keep a
`source` field in SQLite so a web chat and a Code transcript with similar text
remain distinguishable.

The recovery archive should expose:

- `sessions`
- `messages`
- `documents`
- `attachments`
- `projects`
- `memory_items`
- FTS tables or equivalent indexes

After building the database:

```bash
sqlite3 "$RECOVERY_ROOT/archive/claude_recovery.sqlite" \
  'PRAGMA integrity_check; SELECT count(*) FROM sessions; SELECT count(*) FROM messages;'
```

## 4. Recover research files and artifacts

Priorities:

1. Paper sources, TeX, PDFs, figures, result tables, logs, and code.
2. Project instructions and `CLAUDE.md`.
3. Artifact/page HTML, deck JSON, slide text, and speaker notes.
4. Attachments referenced by conversations, with a separate missing list.

For each research project create:

```text
projects/<project>/PROJECT_STATE.md
projects/<project>/SOURCE_LINKS.md
```

`PROJECT_STATE.md` must separate:

- verified results;
- failed experiments;
- formulas or assumptions;
- paper/submission progress;
- open questions;
- next actions;
- evidence paths and hashes.

Never turn a post-turn summary into a fabricated transcript. If only downstream
artifacts exist, label them “downstream evidence,” not “conversation restored.”

Suggested helper scripts from the reference implementation:

```bash
python3 "$RECOVERY_ROOT/tools/normalize_claude_jsonl.py" --help
python3 "$RECOVERY_ROOT/tools/build_conversation_index.py" --help
python3 "$RECOVERY_ROOT/tools/build_search_index.py" --help
python3 "$RECOVERY_ROOT/tools/export_deck_text.py" --help
python3 "$RECOVERY_ROOT/tools/audit_textless_webchats.py" --help
```

These names are examples from the reference pack, not a requirement to copy
the previous user's paths.

## 5. Restore Desktop Code sessions

### 5.1 Inspect index-to-transcript mapping

Read `local_*.json` records and record:

- `sessionId`
- `cliSessionId`
- `cwd` and `originCwd`
- `isArchived`
- `title`
- `sshHost` / SSH metadata, if present
- `sshRemoteTranscriptPath`, if present

Map each `cliSessionId` to a local or remote transcript path. A record without
a body must not be installed as an empty shell.

### 5.2 Isolated test

Use a disposable home or staging directory:

```bash
STAGING="$RECOVERY_ROOT/work/code-pilot-$STAMP"
mkdir -p "$STAGING"
```

Run only after reading the tool source:

```bash
claude-migrate doctor
claude-migrate plan --from <old-account>/<old-org> --to <new-account>/<new-org>
```

Select one root session that:

- is not a spawned child whose parent is absent;
- has a complete transcript;
- does not end in an unsafe pending action;
- has a clear title and a readable final turn.

### 5.3 Production pilot gate

Before writing:

1. Ask the user to fully quit Claude Desktop.
2. Snapshot `claude-code-sessions`.
3. Copy only the index record to staging.
4. Remove obsolete bridge IDs, scheduled task IDs, and unsafe permission
   overrides.
5. Run `plan`, `apply`, and compare the output to the sanitized source.
6. Install only the one generated index.
7. Launch Desktop and verify title, history, tool calls, and input box.
8. Record the exact write set and rollback command.

Only after an explicit user approval, batch the remaining records:

```bash
claude-migrate plan ...
claude-migrate apply --from <old-account>/<old-org> --to <new-account>/<new-org>
```

If the tool supports `undo`, preserve its manifest and test `undo` in staging.
Do not use `claude-transplant --cloud`, `claude-code-export-import
export-cloud`, or any Keychain-reading path.

### 5.4 Verify after a Desktop upgrade

Do not compare the current index bytes to the installation-time hash and call
the session missing. Desktop may rewrite indexes. Instead verify:

- `sessionId`, `cliSessionId`, title, cwd and archive state;
- transcript path exists;
- message count and key tool events parse;
- UI opens and can read the history;
- no unapproved `local_*.json` files appeared.

## 6. Convert web chats into a local Code workspace

This is optional and must remain separate from SSH workspaces.

1. Parse `conversations.json`.
2. Count messages with actual human/assistant text.
3. Exclude textless conversations from the UI conversion; list them in
   `recovery-gaps.md`.
4. Create a local workspace such as:

   ```text
   $RECOVERY_ROOT/Research-Workspace/
   ```

5. Convert each recoverable conversation into a Code-compatible JSONL while
   preserving title, time order, roles, and source UUID.
6. Install `local_*.json` indexes with `cwd` set to the local workspace.
7. Keep personal-life chats archived only when the user asks for cleanup; the
   archive must remain openable.
8. Verify one converted session before batch installation.

Do not claim that a web chat has original Code tool calls, branches, or remote
execution state if the export does not contain them.

In the reference run:

- 119 official web conversations were archived;
- 87 with recoverable body were converted into local Code sessions;
- 26 were left archived as personal-life history;
- 32 had no recoverable human/assistant body and were not converted;
- the local group was named `Research-Workspace`;
- the real SSH group remained `workspace · REMOTE`.

## 7. Old Cowork, Cloud Cowork, and Remote Control

### 7.1 Old local Cowork

Backup the full unit, not just the index:

```text
local-agent-mode-sessions/<account>/<org>/local_<sid>.json
local-agent-mode-sessions/<account>/<org>/local_<sid>/audit.jsonl
local-agent-mode-sessions/<account>/<org>/local_<sid>/outputs/
local-agent-mode-sessions/<account>/<org>/local_<sid>/uploads/
local-agent-mode-sessions/<account>/<org>/local_<sid>/.claude/
```

An index without its body is not a restored task. Test a single non-sensitive
task in a cloned workspace before any UI write.

### 7.2 Cowork VM disk

If a `sessiondata.img` is present, first identify it without mounting:

```bash
file sessiondata.img
xxd -l 64 sessiondata.img
```

If it is an Apple Sparse Image Format (ASIF), copy the original image, expand
only into a scratch directory, run read-only filesystem checks, and search for
the missing session/bridge UUIDs. Record the image hash. Never treat an empty
local VM volume as proof that the cloud never contained the conversation.

### 7.3 Cloud after 2026-10-06

Cloud Cowork and Remote Control may exist only server-side. Without a
legitimate, currently authorized account:

- do not use old cookies, tokens, or Keychain;
- do not call private APIs;
- do not assume a local index has a body;
- record the missing object and draft an official support/export request.

Official `Download task data`, `/port-task-data`, or an authorized
`--teleport` flow may be used only when the user has current access.

## 8. Memory and configuration

### 8.1 Memory

Extract:

- the aggregate memory object;
- per-item memory files;
- project instructions;
- user preferences needed for future work.

Create a reviewable `memory/claude-memory-import.txt` only after removing:

- stale identity claims;
- personal relationships and health-adjacent data;
- addresses and shopping history;
- obsolete institutional affiliations;
- secrets and account identifiers.

Memory import is a cloud write and requires separate approval. It does not
restore chat history.

### 8.2 Configuration

Audit user-level and project-level:

- `CLAUDE.md`
- `settings.json`, `settings.local.json`
- Skills
- Agents
- Commands
- Hooks
- Plugins
- MCP server definitions
- IDE settings
- SSH aliases (redacted)

Generate:

- `configs-redacted/`
- `reports/config-diff.md`
- `reports/config-restore-dry-run.md`

Do not restore `bypassPermissions`, old allowlists, old OAuth, browser
credentials, or connector tokens. A connector must be reauthorized in the
current account UI if still needed.

## 9. Verification and delivery

Run read-only verifiers:

```bash
python3 "$RECOVERY_ROOT/tools/verify_client_sessions.py"
python3 "$RECOVERY_ROOT/tools/audit_config_state.py"
python3 "$RECOVERY_ROOT/tools/audit_recovery_security.py"
python3 "$RECOVERY_ROOT/tools/build_delivery_manifest.py"
```

Then:

```bash
cd "$RECOVERY_ROOT"
shasum -a 256 -c reports/SHA256SUMS.txt
```

For symlink-heavy immutable snapshots, use a Python checker that hashes both
the link text and the resolved target. Never report a symlink as corrupt merely
because plain `shasum -c` cannot read it.

Required reports:

- `coverage.md`: source-by-source counts and the four states;
- `recovery-gaps.md`: missing bodies, missing attachments, deck gaps,
  unverified cloud objects;
- `FINAL-STATUS.md`: what is done, what is pending, what the user must approve;
- `command-log-redacted.md`: operations with secrets removed;
- `security-audit.json`: file count, secret-pattern candidates, permissions;
- `DELIVERY-MANIFEST.json` and `.md`;
- `SHA256SUMS.txt`.

Required UI checks:

- open at least one restored root Code session;
- open at least one converted web chat;
- confirm a new message can be sent in the current account;
- confirm remote Control is off when not needed;
- do not count an old UI screenshot or a local index as cloud synchronization.

## 10. Rollback

Every write batch must have one of:

- a pre-write directory snapshot;
- a target-file list with hashes;
- a tool-generated manifest with an `undo` command;
- an archive-state backup (`archived-sessions.idx` plus changed `local_*.json`).

Before restoring an old snapshot, check whether the app has appended new user
messages since the snapshot. Blindly overwriting can destroy new work.

## 11. Reference instance lessons

The runbook was validated on macOS with Claude Desktop `2.42304.2` and a
legitimate remote SSH workspace:

- 18 old Desktop Code indexes were found;
- 15 had usable bodies and were installed;
- 3 had only index/post-turn summaries and remained gaps;
- 15/15 restored sessions rendered and 15/15 were readable after unarchive;
- 100 remote Code sessions had 100 reachable transcript paths;
- 88 local Research-Workspace sessions were visible;
- 87 web chats were converted; 26 were archived; 32 were textless;
- the SQLite archive contained 435 sessions, 23,760 messages, and 236
  documents with `integrity_check = ok`;
- the final security audit scanned 5,641 files, found 0 secret-pattern
  candidates, and the main manifest checked 5,686 entries with 0 failures.

Important lesson: a free account without Claude Code access can load the local
index but still show a permission/guide screen. Treat that as an account
permission blocker, not a successful migration.

Important lesson: after Desktop upgrade, index hashes may change while the
session remains intact. Verify structure and body reachability, not only bytes.

Important lesson: local and SSH workspaces look similar in the sidebar but are
not interchangeable. Preserve the real execution boundary.
