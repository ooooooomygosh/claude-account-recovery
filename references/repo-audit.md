# 第三方恢复工具兼容性与风险评估

审计日期：2026-10-19

本机环境：macOS 26.5.2 (25F84), arm64

Claude Desktop：`2.42304.2`

审计方式：阅读 README、关键源码和 git 元数据；除 `claude-migrate` 外，未执行未知第三方脚本。`claude-migrate` 已在隔离副本中 dry-run、试点，并经用户批准后用于 15 条本地 Code 会话安装。

## 结论先行

| 工具 | 当前是否建议使用 | 原因 |
|---|---|---|
| `claude-migrate` | **已使用，推荐** | 与 2.42304.2 的本地 Code 索引布局匹配；15/15 安装并在 UI 可读；只复制索引，不碰 transcript、不联网。 |
| `claude-desktop-history` | **只读参考，谨慎** | 存储模型与当前版本一致，但只声明适配 Desktop 2.1.x；Cowork 迁移会改 `cwd`/账号字段，必须先隔离测试。 |
| `agent-history-rescue` | **可用于只读归档，暂不用于本机写入** | 支持官方导出 `conversations.json`，但会把网页对话重建成新的 Code 记录；无法恢复原始 Cloud/Remote Control 正文。 |
| `claude-code-export-import` | **不用于当前任务** | README 只验证到 Desktop 1.40609.x；`export-cloud` 需要旧账号登录和 `claude --teleport`，不符合封禁边界。 |
| `AnthropicReader` | **推荐用于只读浏览** | 单文件离线 HTML，直接读取官方六类 ZIP；不写本地、不上传。 |
| `claude-migration-assistant` | **仅作方法参考** | 浏览器端导出解析器；Memory/Projects 为近似重建，依赖 CDN，不直接写 Desktop。 |
| `claude-transplant` | **不使用** | 本地 move 会搬走记录并可重启 Desktop；`--cloud` 明确读取 Keychain 并访问 claude.ai，禁止使用。 |
| `claude-ai-export` | **不使用** | Chrome 扩展需要登录 claude.ai 才能导出；无法导出 Memory；与旧账号已封禁边界冲突。 |
| `claude-acc` | **禁止用于本任务** | 切换 Desktop 账号、交换凭据、读取 Keychain；用户已明确不改变账号身份。 |

## 逐仓库审计

### 1. onlyilkr/claude-migrate

- Commit：`8a50250df9bc78cd8e5815c6162f5bb163930bcc`
- 最近提交：2026-10-12 `ci: upgrade checkout, setup-go and goreleaser-action; add a release dry run`
- 声明范围：macOS，Claude Desktop Code 本地会话；Cloud、Cowork、claude.ai 聊天、Projects、Artifacts、Memory 不在范围内。
- 关键实现：
  - `internal/store/store.go` 读取 `claude-code-sessions/<account>/<org>/local_*.json`，字段表标注 “as of 2026-10”。
  - `internal/store/fields.go` 包含 `bridgeSessionIds`、`scheduledTaskId`、`cliSessionId`、`priorCliSessionIds`、`postTurnSummary` 等当前记录字段。
  - `apply` 只新增目标记录，不覆盖；manifest 写入前 fsync；`undo` 按 SHA-256 校验后删除。
  - `bridgeSessionIds` 清空，`scheduledTaskId` 移除，`sessionId` 和文件名保留。
- 与 2.42304.2 的兼容性：
  - 本机实际运行 `plan`、`apply`、`undo` 均通过。
  - 15 条有 transcript 的本地 Code 会话全部安装；15/15 在 Desktop 中可打开读取正文。初次安装时 11 条活动、4 条归档；归档的 4 条后来经批准取消归档，最终 15/15 可直接继续。
  - 3 条无 transcript 的 Remote Control 索引未安装，避免生成空壳会话。
- 风险：依赖未公开文件格式；Desktop 更新后应重新 `doctor`。它不能恢复 Cloud/Remote Control 正文。
- 建议：**保留为本次本地 Code 索引恢复的主工具**。回滚只删除 manifest 中本过程新增的 15 个 `local_*.json`，不动旧账号目录、transcript、worktree 或用户文件。

### 2. XDUwt/claude-desktop-history

- Commit：`03b435348e68d472d578a5086903d557e969104a`
- 最近提交：2026-06-09 `docs: add badges ...`
- 声明范围：macOS，Code / Cowork / Chat 三种存储；README 与 LESSONS 明确基于 **Desktop 2.1.x**。
- 关键实现：
  - `02-migrate.sh` 复制 `claude-code-sessions/<old>/<org>/local_*.json` 到新账号。
  - `05-migrate-cowork.sh` 同时复制 `local-agent-mode-sessions/<acct>/<org>/local_<sid>/` 的 body，并改写索引中的 `emailAddress`、`accountName` 和 `cwd` 前缀。
  - `01-backup.sh` 支持 `--full` 打包 `~/.claude/projects`；`03-verify.sh` 检查条数与 transcript 可达性。
  - README 明确 Chat 无法迁移，只能导出归档；Cowork 跨账号恢复“less battle-tested”，建议先用 `--only` 试一条。
- 与 2.42304.2 的兼容性：
  - Code 目录布局与本机观察一致；但仓库没有声明 2.42304.2 实测。
  - Cowork 的 body 目录、`.audit-key`、`cwd` 改写逻辑需要逐项验证；本机旧账号目前只发现 `remote-session-spaces.json` 映射，没有完整 Cowork 正文缓存。
- 风险：`cp -R` 写入、`cwd` 改写、账号字段改写；若 Desktop 运行中执行会被覆写。脚本较老，未覆盖新字段。
- 建议：**只读 `00-inspect.sh` / `01-backup.sh` 可参考；任何 `--apply` 先在隔离 home 中测试，不直接用于生产。**

### 3. HeiGeAi/agent-history-rescue

- Commit：`8685238ea180c7fad4091d8cc6ec2f388a27baaa`
- 最近提交：2026-09-23 `docs: 全渠道更名「黑哥AI」→「问问黑哥」`
- 声明范围：macOS / Windows / Linux；Claude Code、Codex；支持从官方导出 ZIP 恢复。
- 关键实现：
  - `bin/agent-history-rescue.js` 的 `import` 读取 `conversations.json`，生成 Markdown + `conversations.jsonl` 可读存档。
  - `--to claude` 会生成 `local_<uuid>.json`，把网页对话放进 `recovered-claude-history` 项目；`cliSessionId` 由导出 conversation uuid 确定性生成，重复导入不产生重复。
  - 只新增，不删除；App 开着默认停止；有 dry-run 和 restore。
- 与 2.42304.2 的兼容性：
  - 没有声明 2.42304.2 实测；写入字段与 `claude-migrate` 观察到的记录结构相近，但会新建项目目录和记录。
  - 它导入的是网页对话文本，不含原工具调用、分支和 Cloud/Remote Control 会话正文。
- 风险：会改变/新增 Desktop 记录；可能把网页对话标成 Code 会话；标题、时间、cwd 与原始 Desktop 会话不完全一致。
- 建议：**可用来生成只读归档；不要用它替代 `claude-migrate` 恢复原始 Code 索引，也不要用它声称恢复了 3 条 Remote Control 会话。**

### 4. Dangelo123/claude-code-export-import

- Commit：`9cec2b21a5c8ad9c84ca596da05d26a1333babd3`
- 最近提交：2026-10-07 `fix(export-cloud): swap the longest scratch path first`
- 声明范围：Linux / Windows / macOS；README 明确 “Verified against Claude Desktop 1.40609.x (Linux)”，并声明不保证未来版本。
- 关键实现：
  - `claude_session_port.py` 识别 `~/.claude/projects/<ENC(cwd)>/<sessionId>.jsonl` 和 `claude-code-sessions/<account>/<group>/local_*.json`。
  - `export` 打包 transcript + sidecar + `meta.json`；`import` 生成新 session id，重写 `cwd`，写两份记录。
  - `export-cloud` 先运行 `claude -p /exit --teleport <session>`，需要拥有该会话的 claude.ai 账号登录；API key 不够。
  - `batch.py` 可迁移整个安装、memories、`CLAUDE.md`。
- 与 2.42304.2 的兼容性：
  - 路径探测覆盖 macOS，但未在 2.42304.2 验证；记录字段可能少于当前 Desktop 版本。
  - `export-cloud` 与封禁账号边界冲突：必须先登录旧账号，不能使用。
- 风险：`import` 会生成新 ID，可能破坏原始会话 ID/pin；`export-cloud` 需要旧账号认证。
- 建议：**不用于当前恢复**。如果未来要迁移单条本地 Code 会话到另一台机器，可作为备选，但先 dry-run + 隔离测试。

### 5. PiniShv/AnthropicReader

- Commit：`c261d19a42f9f449b65ca6863e5c56eeff46cfbb`
- 最近提交：2026-10-07 `Scripts: no page code built from data at the last two places`
- 声明范围：浏览器端单文件 HTML；读取官方导出 `conversations-*`、`light_metadata-*`、`projects-*`、`memories-*`、`design_chats-*`、`frames-*`、`manifest-*`。
- 关键实现：
  - `dist/claude-export-reader.html` 是离线单文件；无网络请求、无分析、无 CDN。
  - 使用 DOMPurify 清理导出文本；HTML artifact 在 sandbox iframe 中运行，不带 `allow-same-origin`。
  - 明确列出导出不包含的内容：上传文件、代码生成的二进制、项目与会话之间的链接、部分 artifact 共享存储、隐藏 thinking 全文等。
- 与 2.42304.2 的兼容性：与 Desktop 版本无关；只依赖导出格式，适合当前六类 ZIP。
- 风险：导出数据含姓名、邮箱、电话；必须在本地打开，不能上传；远程图片不自动加载。
- 建议：**推荐用于人工浏览与全文搜索**；与 SQLite 档案互补。

### 6. ukogan/claude-migration-assistant

- Commit：`42feb750522a4ee56ddc306c70d19d61c3fd2990`
- 最近提交：2026-02-13 `fix(admin): include user projects in migration package output`
- 声明范围：浏览器端静态 SPA；个人导出 ZIP 或 Team admin JSON。
- 关键实现：
  - `js/processing/zip-reader.js` 解析导出；`conversation-parser.js`、`artifact-extractor.js` 生成迁移文档。
  - Memory 为“近似”重建；Projects 为“近似”手工重建；knowledge files 仅在拥有原文件时精确。
  - 依赖 CDN 的 JSZip、Lucide、Marked；不是完全离线。
- 与 2.42304.2 的兼容性：不直接写 Desktop；与 Desktop 版本无关。
- 风险：CDN 依赖、Memory/Projects 近似、不能恢复 Cloud 线程；导出的“迁移文档”不能当作原始数据。
- 建议：**仅作方法参考**；不用于本任务的生产恢复。

### 7. vitaliyhayda/claude-transplant

- Commit：`c24ea1c2cc973fe4a40f0a5501ca43828b28ff48`
- 最近提交：2026-10-15 `fix: finish cloud cleanup and batch restart moves`
- 声明范围：macOS；Claude Desktop Code；本地 move + `--cloud` Remote Control reconcile。
- 关键实现：
  - 本地 move 是“搬走”而非复制：把源记录放入 quarantine，保留同一 `cliSessionId`，可 `undo`。
  - `--cloud` 从 Keychain 读取 Desktop 的 claude.ai session，在内存中向 `claude.ai` 发请求，归档/恢复 Remote Control mirror。
  - menubar 的 Move 总是带 `--cloud`。
- 与 2.42304.2 的兼容性：README 与源码针对 2026-09/10 的 Desktop 布局，理论上接近；但本任务不需要它的 move 语义。
- 风险：高。移动会改变源账号可见性；`--cloud` 触碰 Keychain、访问 claude.ai，可能被解释为规避封禁或复用旧凭据。
- 建议：**禁止使用 `--cloud` 和 menubar Move**；本地 move 也不建议，因为 `claude-migrate` 的加法复制更安全。

### 8. selan-ai/claude-ai-export

- Commit：`d6828c9919658b24a2003c1755b4b12ab3288f2a`
- 最近提交：2026-08-29 `Link the published Chrome Web Store listing`
- 声明范围：Chrome/Edge/Brave/Arc 扩展，导出 claude.ai 聊天、Projects、附件、定时任务；导入 Desktop 内置 importer。
- 关键实现：
  - 扩展只允许 `https://claude.ai/*`，使用浏览器现有登录（`credentials: 'include'`），不读取/存储 session cookie。
  - 导入依赖 Desktop 的 `Settings → Import & export → Import…`；Chats 会变成 sidebar 会话，Projects 变成 Spaces；Memory 无法导出。
  - 定时任务由 `scripts/import.sh` 单独写本地 JSON + skill 文件。
- 与 2.42304.2 的兼容性：依赖 Desktop 内置 importer；当前版本是否有该入口需在 UI 验证；未在本机执行。
- 风险：必须登录 claude.ai 旧账号才能导出；与旧账号已封禁冲突；Memory 不可导出；导入是一次性副本。
- 建议：**不使用**。官方导出 ZIP 已足够，且不需要重新登录旧账号。

### 9. ohmaseclaro/claude-acc

- Commit：`eea0659eff2f62fe376ca9a4570dccae37ad0d63`
- 最近提交：2026-08-04 `feat: converge a renamed routine's title across accounts`
- 声明范围：切换 Claude Desktop 保存的账号，合并本地历史，交换凭据。
- 关键实现：
  - `switch` 会合并 `claude-code-sessions` 和 `scheduled-tasks.json`，退出 Desktop，交换 `config.json` 的 OAuth token、Cookies、Local Storage、Session Storage、IndexedDB，删除 `bridge-state.json`，再重启。
  - `list` 会解密 Desktop token 查询 quota；`publish_cli_credentials` 会读写 `~/.claude/.credentials.json`。
- 与 2.42304.2 的兼容性：仓库声明 Desktop-only，但当前任务不需要切换账号。
- 风险：极高。改变账号身份、复用/交换旧凭据、触碰 Keychain、删除 bridge 状态，均违反用户规则。
- 建议：**禁止使用**。不要用它“切回旧账号”或“合并账号”。

## 与当前 Desktop 2.42304.2 的总体判断

1. **本地 Code 索引恢复**：`claude-migrate` 是唯一在本机 2.42304.2 上完成端到端验证的工具。它只处理 `claude-code-sessions` 索引，不处理 Cloud/Remote Control 正文。
2. **官方导出浏览**：`AnthropicReader` 最安全；`agent-history-rescue` 的只读归档模式可作补充。
3. **Cowork**：`claude-desktop-history` 的模型最完整，但只声明 2.1.x；当前旧账号未发现完整 Cowork body，暂不写入。
4. **Cloud / Remote Control**：没有任何工具能在不登录旧账号、不读 Keychain 的前提下恢复服务端正文。`claude-transplant --cloud`、`claude-code-export-import export-cloud`、`claude-ai-export` 均越界。
5. **Memory / Projects / Artifacts**：官方导出可读；写入新账号必须走新账号的合法导入/重建路径，不能用旧 Token 或旧 Cookie。

## 证据与限制

- 本报告只基于 README、源码和 git 元数据；除 `claude-migrate` 外，未执行第三方脚本。
- 未对任何仓库运行网络请求、Keychain 读取、账号切换或 Cloud teleport。
- 兼容性判断以“是否匹配当前本机目录/字段/实际验证”为准，不把 README 的声明当作实测。
- 任何未来写入前仍需：完整退出 Desktop、隔离 home dry-run、生成 manifest、保留可回滚快照。
