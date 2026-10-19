---
name: claude-account-recovery
description: >-
  Recovers Claude Desktop Code and Cowork history, official-export web chats,
  Projects, Artifacts, Memory, research files, and redacted configuration after
  a Claude account is deleted, disabled, or replaced. Use for local JSONL/index
  restoration, claude.ai export recovery, SSH-hosted Claude sessions, or a
  migration runbook. Never use it to reuse old credentials, evade a ban, or
  claim that a local restore is a cloud migration.
---

# Claude Account Recovery

## 目标

当旧 Claude Cloud 账号已经被删除、停用或无法登录时，从用户合法持有的
本机数据、官方导出和已授权 SSH 主机中，尽可能恢复：

- 对话正文、标题、时间线、分支、工具调用和工作目录；
- Desktop Code 的本地索引与 transcript；
- 网页 Chat、Projects、Artifacts、Pages、Decks 和附件；
- Memory、`CLAUDE.md`、Skills、Agents、Commands、Hooks、MCP 与 IDE 配置；
- 科研代码、论文、公式、实验记录、失败结果和下一步计划；
- 可离线检索的数据库、覆盖报告、缺口清单和可回滚的迁移包。

最终产物必须独立于旧账号。可以恢复“本地可读”和“新账号中可继续”，
但不能把二者说成“Anthropic 云端已原生迁移”。

## 适用与不适用

适用：

- Claude Desktop Code 会话索引存在，但新账号侧栏不显示；
- 有官方六类导出 ZIP，或只有 `conversations.json`；
- 旧 Desktop、`~/.claude`、Cowork VM 或已授权的 SSH 主机仍有数据；
- 需要把网页 Chat 转成本地可打开的 Code 会话；
- 需要恢复科研文件、检索库、配置模板和可回滚迁移包。

不适用：

- 用旧 Token、Cookie、OAuth、Keychain 或 API Key 登录旧账号；
- 绕过封禁、切换账号身份或模拟客户端；
- 在没有账号授权的情况下读取云端私有对象；
- 把不存在的消息、实验结果或“已同步”状态编造出来。

## 不可混淆的四种状态

每次报告都要分别写清：

| 状态 | 判定 |
|---|---|
| 本地可读 | 原始 JSONL/JSON/Markdown 可解析，正文可打开 |
| Desktop UI 可见 | 新账号索引已加载，侧栏出现正确标题 |
| 可继续使用 | 打开后有完整历史，输入框可用，上下文可接续 |
| 云端已同步 | Anthropic 服务端原生持有该历史；没有账号级验证就不能声称 |

另外区分：文件已备份、Project 已归档、Memory 已生成导入草稿、配置已脱敏，
它们都不等于会话已恢复或已同步。

## 先读什么

- 执行完整恢复流程前，读
  [references/recovery-runbook.md](references/recovery-runbook.md)。它包含
  P0–P7 的命令、目录、数据模型、验收和回滚方法。
- 运行任何第三方仓库前，读
  [references/repo-audit.md](references/repo-audit.md)。其中记录了 9 个仓库的
  commit SHA、兼容版本、实际验证结果和禁用项。
- 需要原始任务约束的脱敏版本时，读
  [references/recovery-brief.md](references/recovery-brief.md)。它保留了本次恢复的
  授权、隐私、封禁和分阶段边界，但移除了个人与机构信息。
- 需要复现本次环境时，读
  [references/reference-instance.md](references/reference-instance.md)。它记录
  macOS、Claude Desktop 2.42304.2、SSH 工作区、网页导出和新账号的实测结果。

## 数据层模型

不要把所有来源拼成一个“聊天数据库”。至少保留以下独立层：

1. **官方网页导出**：`conversations-*.zip`、`projects-*.zip`、
   `memories-*.zip`、`frames-*.zip`、`light_metadata-*.zip`、
   `feedback-*.zip`。这是离线档案，不是 Desktop Code 索引。
2. **Desktop Code 本地索引**：
   `~/Library/Application Support/Claude/claude-code-sessions/<account>/<org>/local_*.json`。
3. **Code transcript**：
   `~/.claude/projects/<encoded-cwd>/<cliSessionId>.jsonl`，可在本机或 SSH 主机。
4. **旧版 Cowork**：
   `local-agent-mode-sessions/<account>/<org>/local_<sid>/` 下的索引、
   `audit.jsonl`、`outputs/`、`uploads/` 和 `.claude/`。
5. **2026-10-06 之后的 Cloud Cowork / Remote Control**：可能只在服务端，
   本地导出不一定有正文；没有当前账号授权就只能列缺口。
6. **CLI、SDK、自动研究和子代理**：可作科研证据和检索材料，但不要伪装成
   用户的 Desktop UI 会话。

### 为什么不能把本地会话塞进 SSH workspace

Desktop workspace 绑定 `cwd` 和运行环境。`workspace · REMOTE` 这类组代表远程
SSH 工作区，本地网页聊天或本地文件没有对应的远程 transcript。强行改写
`cwd` 会让客户端到服务器寻找不存在的历史，破坏“可继续”验收。

正确做法是保留两个真实分组，例如：

- `Research-Workspace`：本机恢复和网页聊天转换出的本地 Code 会话；
- `workspace · REMOTE`：真实 SSH Code 会话。

两者可以出现在同一侧栏、使用同样的打开和继续交互，但不能伪装成同一个
执行环境。

## 强制工作顺序

1. **冻结范围与授权**：确认导出目录、Mac 数据源、是否允许 SSH、目标账号
   是否有合法 Claude Code 权限。不要索取密码；私钥只在用户已授权的 SSH
   范围内使用。
2. **只读盘点**：记录路径、大小、数量、哈希、时间线和缺失项；不执行清理、
   不覆盖、不启动写入脚本。
3. **原样备份**：用 `ditto`/`cp -p` 复制到私有 `source-immutable/`，
   权限 `700`，为关键文件生成 SHA-256。含凭据的目录只做私有快照，不做
   pattern scan 的公开报告。
4. **导出解析**：先 `unzip -l` 检查路径穿越、异常软链和压缩炸弹，再在沙盒
   目录解压；保留 ZIP 哈希和原始文件名。
5. **规范化与去重**：以会话 UUID、CLI session ID、内容哈希去重；保留来源
   标记、分支、消息顺序、工具调用和附件引用，不把不同来源合并成一条。
6. **恢复科研资料**：先建立可搜索的离线档案，再处理 Desktop UI。项目状态
   要写明目标、已有结果、失败实验、关键公式、论文进度和下一步；不补造结果。
7. **恢复 Desktop Code**：先 `doctor`/`plan`，在隔离 home 中测试，选一条
   根会话试点；完全退出 Desktop，快照索引，再经用户明确批准后分批 `apply`。
8. **处理 Cowork/Cloud**：旧 Cowork 只恢复可证明的索引和正文；Cloud/Remote
   Control 只能走当前账号的合法官方路径，不能使用旧认证。
9. **配置与 Memory**：区分用户级和项目级；生成脱敏 diff 和模板。Memory 先
   生成候选导入文件，默认不写入云端。
10. **验收与交付**：分别验证本地可读、UI 可见、可继续、云端状态；生成覆盖
    报告、缺口报告、回滚说明、哈希清单和最终 manifest。

## 第三方工具选择

| 工具 | 使用方式 |
|---|---|
| `onlyilkr/claude-migrate` | Desktop Code 本地索引的首选；先 `doctor`/`plan`，隔离测试后 `apply`，保留 `undo` 与 pre-apply 快照 |
| `PiniShv/AnthropicReader` | 官方六类 ZIP 的离线只读浏览；在本地浏览器打开，不上传 |
| `XDUwt/claude-desktop-history` | 旧 Code/Cowork 存储的只读诊断和备份参考；当前 Desktop 版本未声明适配，生产写入需隔离测试 |
| `HeiGeAi/agent-history-rescue` | 官方导出转 Markdown/JSONL 的只读归档参考；不要用它替代原始 Code 索引恢复 |
| `Dangelo123/claude-code-export-import` | 跨机器 transcript/path-map 分析参考；`export-cloud` 需要旧账号认证，默认禁用 |
| `ukogan/claude-migration-assistant` | Projects/Memory 重建方法参考；输出是近似材料，不是原始数据 |
| `vitaliyhayda/claude-transplant` | 不用于本流程；其 `--cloud` 读取 Keychain 并访问 claude.ai |
| `selan-ai/claude-ai-export` | 不使用；需要旧 claude.ai 登录，且不能导出 Memory |
| `ohmaseclaro/claude-acc` | 禁止使用；切换账号、交换凭据、读 Keychain |

所有仓库先记录 `git rev-parse HEAD`，再阅读 README、关键源码和写入路径。
不要执行 `curl | bash`、未审计的 `npx -y github:...` 或远程二进制。

## 最小安全契约

- 原始资料只读；第一个写操作前必须有完整快照。
- 任何 `--apply`、`import-all`、`--to claude`、修改索引或重建 Cowork 都是
  dry-run 后等待明确批准。
- 不在 Claude Desktop 运行时写 `claude-code-sessions`；先用 Cmd+Q 完全退出。
- 不修改 `~/.claude/settings.json`、认证配置、Keychain 或旧账号 Token。
- 不把私有科研资料、邮件、电话、OAuth、Cookie、API Key 上传或提交 Git。
- 不对原始科研仓库做 `reset --hard`、清理、移动或删除。
- 测试消息、归档状态和索引写入都要写入变更报告；失败要可回滚。
- 最终必须明确写出“本地恢复，不等于云端同步”以及无法恢复项。

## 交付结构

在用户指定目录（默认 `~/Documents/Claude-Recovery/`）构建：

```text
Claude-Recovery/
├── source-immutable/      # 原始快照、官方 ZIP、哈希
├── conversations/         # 网页聊天 Markdown/JSON 只读副本
├── normalized/            # 规范化 JSON/Markdown
├── sessions/              # Desktop Code、SSH、Cowork 分层
├── projects/              # 按科研项目整理的状态与证据
├── artifacts/             # Pages、Artifacts、Decks、附件
├── memory/                # 原始 Memory、脱敏导入草稿、排除项
├── configs-redacted/      # Skills、MCP、Hooks、SSH、IDE 模板
├── archive/               # SQLite FTS、构建和搜索脚本
├── reports/               # 覆盖、缺口、验收、安全审计、manifest
├── rollback/              # dry-run、快照和可逆操作工具
├── tools/                 # 可重复运行的恢复脚本
└── Research-Workspace/    # 可在 Desktop Code 打开的本地工作区
```

`Research-Workspace` 应包含 `CLAUDE.md`、项目目录、会话清单、检索入口和
原始导出副本；不要把它直接指向含凭据的 `source-immutable/live-*`。

## 验收门槛

恢复完成至少需要：

- 导出卷数量、大小、SHA-256 与原始副本一致；
- 所有索引和 JSONL 可解析，记录数与清单一致；
- 每条恢复的 Code 会话能在 Desktop 中打开，标题、正文和工具历史正确；
- 试点的“新账号回复”只作为 UI 可继续证据，不作为云端同步证据；
- `source-immutable` 和交付包通过哈希校验；符号链接按目标而非链接文本校验；
- SQLite `PRAGMA integrity_check` 为 `ok`，且会话、消息、文档数量写入报告；
- 生成 `coverage.md`、`recovery-gaps.md`、`FINAL-STATUS.md`、
  `DELIVERY-MANIFEST.*`、`SHA256SUMS` 和回滚说明；
- 对缺失正文、空导出、源缺口和未验证云端项逐条列出，不伪造空壳会话。

## 快速路由

- 只有官方 ZIP：先做离线档案和检索库，不碰 Desktop。
- 有 Desktop Code 旧索引：先检查 `local_*.json` 与 `cliSessionId` 的映射，
  再决定是否安装索引。
- 有 SSH 权限：只读取用户自己的 `~/.claude/projects/`、项目和会话索引，
  不下载大型实验数据。
- 旧账号被封：不登录旧账号；优先离线恢复和联系 Anthropic 补充导出。
- 用户要求“全部恢复到新客户端”：先完成本地归档和一条试点，明确批准后再
  分批写入，并持续区分本地可见、可继续和云端已同步。
