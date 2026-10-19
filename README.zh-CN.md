# Claude Account Recovery Skill

[English](README.md) | 简体中文

一个用于 **Claude 账号被删除、停用、封禁或更换后，从本机和官方导出中恢复
Claude Desktop Code、网页聊天、科研文件、Memory、Projects 和配置** 的 Codex
Skill。

它不是“绕过封禁”的工具，也不使用旧账号 Token、Cookie、OAuth、Keychain
或 API Key。它的目标是把用户合法持有的数据变成独立、可检索、可验证、
可回滚的本地恢复包，并在新账号具备合法权限时，把可恢复的会话接回
Claude Desktop Code。

## 1. 这是干什么的，有什么用？

Claude 的不同历史并不是同一份数据：

- `claude.ai` 网页聊天在官方导出 ZIP 中；
- Desktop Code 会话由本地 `local_*.json` 索引和 JSONL transcript 组成；
- Cowork 还有自己的索引、`audit.jsonl`、输出和上传目录；
- Cloud Cowork、Remote Control 和定时任务可能只在服务端；
- Projects、Artifacts、Memory、Skills 和配置又属于不同存储层。

账号消失后，直接“复制一个数据库”通常会失败：索引存在但没有正文、
正文存在但没有侧栏索引、网页聊天不是 Code transcript、远程 workspace
又和本地 workspace 绑定不同执行环境。

这个 Skill 提供的是一套经过实际验证的恢复流程：

- 先只读盘点，再原样备份；
- 解析官方导出并建立离线检索库；
- 恢复科研文件、项目状态、Artifacts 和 Memory 草稿；
- 用隔离测试和单条试点恢复 Desktop Code；
- 将网页聊天转换为独立的本地 Code 会话；
- 严格区分本地可读、Desktop UI 可见、可继续和云端已同步；
- 输出覆盖报告、缺口清单、哈希、回滚和最终交付包。

适用于：

- 旧 Claude 账号无法再登录；
- 仍有官方数据导出 ZIP；
- Mac 上还有 `~/.claude` 或 Claude Desktop 数据；
- 有授权的 SSH 科研主机或远程 Code 会话；
- 新账号有合法 Claude Code 权限，希望恢复部分历史。

不适用于：

- 绕过账号封禁；
- 用旧凭据重新登录；
- 切换账号身份或读取 Keychain；
- 伪造不存在的聊天、实验结果或“云端已同步”。

## 2. 效果是什么？

效果不是“把所有东西塞进一个文件夹”，而是生成一个可以审计、搜索、
打开和回滚的恢复包。

在用于构建本 Skill 的参考实例中：

| 项目 | 实测结果 |
|---|---:|
| 旧 Desktop Code 索引 | 18 |
| 有正文并恢复的会话 | 15 |
| 恢复后可读 | 15/15 |
| 恢复后可继续 | 15/15 |
| 只有索引、没有正文 | 3 |
| 远程 Code transcript 路径核验 | 100/100 可达 |
| 本地恢复工作区会话 | 88 |
| 官方网页聊天 | 119 |
| 网页聊天转换成本地 Code 会话 | 87 |
| 没有可恢复正文的网页聊天 | 32 |
| 默认归档的个人生活类聊天 | 26 |
| SQLite 检索库 | 435 会话、23,760 消息、236 文档 |
| SQLite 完整性 | `ok` |
| 最终交付哈希校验 | 5,686 项，0 失败 |

参考实例已验证：

- 恢复的 Code 会话能在侧栏打开；
- 原历史、工具调用和上下文可读取；
- 新账号可以在同一上下文中继续输入；
- 网页聊天可以在单独的本地工作区打开和继续；
- 文件面板能看到科研项目、原始导出、报告和检索入口。

这些数字是参考结果，不是对所有 Claude 版本的保证。Desktop 存储格式
可能随版本变化，必须重新运行 `doctor`、隔离测试和 UI 验收。

## 3. 需要什么输入？

### 必需

- 一个合法持有的 Claude 官方导出目录，通常包含：
  - `conversations-*.zip`
  - `projects-*.zip`
  - `memories-*.zip`
  - `frames-*.zip`
  - `light_metadata-*.zip`
  - `feedback-*.zip`
- 或至少一个可解析的 `conversations.json`
- macOS 上可访问的 Claude 数据，例如：
  - `~/.claude/`
  - `~/.claude.json`
  - `~/Library/Application Support/Claude/`
  - 项目目录中的 `.claude/`、`CLAUDE.md`、`.mcp.json`
- 一个独立的恢复输出目录
- 足够的磁盘空间用于不可变备份和转换后的副本

### 可选

- 用户明确授权的 SSH 主机和只读会话目录；
- 新账号的合法 Claude Code 权限；
- 需要恢复的项目目录、Git 仓库和 worktree；
- 对生产 Desktop 索引写入的明确批准。

### 永远不需要

- 旧账号密码；
- 旧 OAuth、Cookie、API Key；
- Keychain 内容；
- 旧 SSH 私钥明文；
- 上传到第三方网站的研究资料。

## 4. 最后得到什么结果？

默认输出结构：

```text
Claude-Recovery/
├── source-immutable/      # 原始快照、官方 ZIP、哈希
├── conversations/         # 网页聊天只读 Markdown/JSON
├── normalized/            # 规范化会话数据
├── sessions/              # Desktop Code、SSH、Cowork 分层
├── projects/              # 科研项目状态、证据和下一步
├── artifacts/             # Pages、Decks、Artifacts、附件
├── memory/                # Memory 原文、脱敏导入草稿、排除项
├── configs-redacted/      # Skills、MCP、Hooks、IDE 配置模板
├── archive/               # SQLite 全文检索库
├── reports/               # 覆盖、缺口、验收、安全和 manifest
├── rollback/              # dry-run、快照和回滚工具
├── tools/                 # 可重复运行的恢复脚本
└── Research-Workspace/    # 可在 Desktop Code 打开的本地工作区
```

最终报告会分别给出：

1. **本地可读**：原始数据是否完整、可解析；
2. **Desktop UI 可见**：新账号侧栏是否出现正确会话；
3. **可继续使用**：是否能打开完整历史并继续输入；
4. **云端已同步**：是否有服务端级证据。

第 4 项不会因为本地恢复或 UI 显示而自动成立。没有账号级验证时，
报告会明确写 `not verified`。

此外还会得到：

- `coverage.md`：来源、数量、恢复率和四态；
- `recovery-gaps.md`：3 条正文缺口、空导出、附件和 deck 缺口；
- `FINAL-STATUS.md`：已完成、未完成和待批准事项；
- `DELIVERY-MANIFEST.*` 与 `SHA256SUMS`；
- 回滚快照和逐文件变更清单；
- 不含旧凭据的配置模板；
- 可被后续 Codex/Agent 继续使用的研究项目状态。

## 安装

如果使用 Codex：

```bash
git clone https://github.com/oooooomygosh/claude-account-recovery.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/claude-account-recovery"
```

然后调用：

```text
$claude-account-recovery
```

不需要安装依赖。仓库本体就是 Skill 目录，`SKILL.md` 是入口。

## 快速使用

```text
$claude-account-recovery 帮我恢复旧 Claude 账号的资料。
官方导出在 /path/to/export，Mac 数据在默认位置。
先只读盘点并生成恢复计划，不要修改 Claude Desktop。
```

如果要接入 SSH：

```text
$claude-account-recovery 已授权 SSH 主机 example-host。
只读取我的 ~/.claude/projects 和项目索引，不下载大型实验数据。
```

如果要写入新账号的 Desktop：

```text
$claude-account-recovery 先做隔离 dry-run，再选择一条安全的根会话试点。
未看到试点结果和回滚清单前，不要批量写入。
```

## 仓库结构

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

### 核心文件

- `SKILL.md`：目标、适用边界、数据层、强制顺序、工具选择、验收门槛；
- `references/recovery-runbook.md`：P0–P7 详细命令、备份、索引恢复和回滚；
- `references/repo-audit.md`：9 个第三方仓库的 commit、兼容性和禁用项；
- `references/reference-instance.md`：参考实例的实测结果；
- `references/recovery-brief.md`：脱敏后的 Agent 主任务书。

## 安全边界

- 不读取或复用旧账号认证材料；
- 不自动登录、登出或改账号；
- 不执行未经审计的第三方脚本；
- 不覆盖或清理原始数据；
- 不把本地恢复说成云端迁移；
- 不把缺失正文伪造成空会话；
- 不上传私有科研资料或个人敏感信息。

## 验证

```bash
python3 scripts/validate_skill.py .
```

校验内容：

- `SKILL.md` frontmatter；
- 必需字段；
- 内部链接；
- 未完成占位符；
- 基础的敏感字符串模式。

## 许可证

MIT。第三方工具、官方文档和导出格式归各自权利人所有。
