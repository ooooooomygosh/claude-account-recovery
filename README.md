# Claude Account Recovery Skill

English | [简体中文](README.zh-CN.md)

A Codex skill for recovering **Claude Desktop Code and Cowork history,
official-export web chats, research files, Projects, Artifacts, Memory, and
redacted configuration** after a Claude account is deleted, disabled, banned,
or replaced.

This is not a ban-evasion tool. It does not reuse old OAuth, cookies, tokens,
Keychain entries, API keys, or private keys. It turns lawfully accessible local
and exported data into an independent, searchable, verifiable, and reversible
recovery pack, then optionally restores resumable sessions into a legitimately
authorized Claude Desktop account.

## 1. What It Does and Why It Matters

Claude history is not one database:

- web chats live in official export ZIPs;
- Desktop Code sessions combine `local_*.json` indexes with JSONL transcripts;
- Cowork has separate indexes, `audit.jsonl`, outputs, and uploads;
- Cloud Cowork and Remote Control may exist only server-side;
- Projects, Artifacts, Memory, Skills, and settings use different stores.

After account loss, simply copying one directory usually fails because the
index, body, workspace, and execution environment may come from different
layers.

This skill provides a tested workflow to:

- inventory everything read-only before changing it;
- create immutable, hashed backups;
- parse official exports into a searchable offline archive;
- recover research files, project state, Artifacts, and Memory drafts;
- restore Desktop Code sessions through isolated tests and a one-session pilot;
- convert recoverable web chats into a separate local Code workspace;
- distinguish local readability, UI visibility, resumability, and cloud sync;
- deliver coverage reports, gaps, checksums, rollback instructions, and a
  final recovery package.

Use it when:

- the old Claude account can no longer be accessed;
- an official export is available;
- Mac-side Claude/Desktop data still exists;
- an authorized SSH research host contains remote sessions;
- a current account has legitimate Claude Code access.

Do not use it to:

- bypass an account restriction;
- reuse old credentials;
- switch account identity;
- fabricate sessions, research results, or cloud-sync claims.

## 2. What Effect It Produces

The result is not just a folder dump. It is an auditable and resumable recovery
package.

Reference-instance results:

| Metric | Result |
|---|---:|
| Old Desktop Code indexes | 18 |
| Sessions with recoverable bodies | 15 |
| Sessions readable after restore | 15/15 |
| Sessions resumable after restore | 15/15 |
| Indexes without bodies | 3 |
| Remote transcript paths verified | 100/100 |
| Sessions in the local recovery workspace | 88 |
| Official web conversations | 119 |
| Web conversations converted to local Code sessions | 87 |
| Web conversations without recoverable body text | 32 |
| Personal-life chats archived by default | 26 |
| SQLite search archive | 435 sessions, 23,760 messages, 236 documents |
| SQLite integrity | `ok` |
| Final delivery checksums | 5,686 checked, 0 failed |

In the reference run, restored sessions opened with their original history and
tool context, new messages could be sent in the current account, converted web
chats were independently resumable, and the research file pane exposed the
recovery archive.

These metrics are evidence from one verified environment, not a guarantee for
future Claude Desktop versions. Re-run version checks, isolated tests, and UI
acceptance every time.

## 3. Required Inputs

Required:

- a lawfully held official Claude export, normally containing:
  - `conversations-*.zip`
  - `projects-*.zip`
  - `memories-*.zip`
  - `frames-*.zip`
  - `light_metadata-*.zip`
  - `feedback-*.zip`
- or at least a parseable `conversations.json`;
- access to authorized Mac-side data such as:
  - `~/.claude/`
  - `~/.claude.json`
  - `~/Library/Application Support/Claude/`
  - project-level `.claude/`, `CLAUDE.md`, and `.mcp.json`;
- a separate recovery output directory;
- enough disk space for immutable backups and derived copies.

Optional:

- an explicitly authorized SSH host and read-only session/project paths;
- a current account with legitimate Claude Code access;
- research repositories and Git worktrees;
- explicit approval for writes to the live Desktop index.

Never provide:

- old passwords;
- old OAuth, cookies, or API keys;
- Keychain contents;
- private SSH key material in a public report;
- private research data for upload to a third-party service.

## 4. Final Result

Default output:

```text
Claude-Recovery/
├── source-immutable/      # original snapshots, official ZIPs, hashes
├── conversations/         # readable web-chat copies
├── normalized/            # normalized JSON/Markdown
├── sessions/              # Desktop Code, SSH, and Cowork layers
├── projects/              # research state, evidence, and next actions
├── artifacts/             # Pages, decks, artifacts, attachments
├── memory/                # originals, redacted import draft, exclusions
├── configs-redacted/      # Skills, MCP, Hooks, IDE templates
├── archive/               # SQLite FTS/search archive
├── reports/               # coverage, gaps, acceptance, security, manifest
├── rollback/              # dry-run and reversible operations
├── tools/                 # reusable recovery scripts
└── Research-Workspace/    # local workspace openable in Desktop Code
```

The final report separates:

1. **Local readable** — original data is present and parseable;
2. **Desktop UI visible** — the target account shows the session;
3. **Resumable** — full history opens and a new message can be sent;
4. **Cloud synchronized** — server-side ownership is actually verified.

The fourth state is never inferred from the first three. If no account-level
verification exists, the report says `not verified`.

Delivered artifacts include:

- `coverage.md`;
- `recovery-gaps.md`;
- `FINAL-STATUS.md`;
- `DELIVERY-MANIFEST.*`;
- `SHA256SUMS`;
- rollback snapshots and changed-file lists;
- redacted configuration templates;
- project-state documents suitable for continuing research.

## Install

For Codex:

```bash
git clone https://github.com/oooooomygosh/claude-account-recovery.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/claude-account-recovery"
```

Invoke:

```text
$claude-account-recovery
```

No runtime dependencies are required. The repository root is the skill folder;
`SKILL.md` is the entrypoint.

## Quick Start

```text
$claude-account-recovery Recover my old Claude account data.
The official export is at /path/to/export and the Mac data is in its default
location. Start with a read-only inventory and a recovery plan. Do not modify
Claude Desktop yet.
```

For an authorized remote host:

```text
$claude-account-recovery The SSH host example-host is authorized.
Read only my ~/.claude/projects and project indexes. Do not download large
experiment outputs.
```

For a production UI restore:

```text
$claude-account-recovery Run an isolated dry run and select one safe root
session for a pilot. Do not batch-write until I have reviewed the pilot,
the write set, and the rollback plan.
```

## Repository Layout

```text
.
├── SKILL.md
├── README.md
├── README.zh-CN.md
├── LICENSE
├── agents/
│   └── openai.yaml
├── references/
│   ├── recovery-runbook.md
│   ├── repo-audit.md
│   ├── reference-instance.md
│   └── recovery-brief.md
└── scripts/
    └── validate_skill.py
```

## Safety

- no old credential reuse;
- no automatic login, logout, or account switching;
- no unaudited third-party write scripts;
- no deletion or cleanup of original evidence;
- no claim that local recovery equals cloud migration;
- no empty shells to improve recovery statistics;
- no upload of private research or personal data.

## Validation

```bash
python3 scripts/validate_skill.py .
```

The validator checks the `SKILL.md` frontmatter, links, unfinished
placeholders, and a few basic sensitive-string patterns.

## License

MIT. Third-party tools, official documentation, and export formats remain the
property of their respective owners.
