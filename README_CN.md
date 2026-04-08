[![License](https://img.shields.io/github/license/giuseppe-trisciuoglio/developer-kit.svg)](./LICENSE)
[![Security Scan](https://github.com/giuseppe-trisciuoglio/developer-kit/actions/workflows/security-scan.yml/badge.svg)](https://github.com/giuseppe-trisciuoglio/developer-kit/actions/workflows/security-scan.yml)
[![Plugin Validation](https://github.com/giuseppe-trisciuoglio/developer-kit/actions/workflows/plugin-validation.yml/badge.svg)](https://github.com/giuseppe-trisciuoglio/developer-kit/actions/workflows/plugin-validation.yml)
[![Skills](https://img.shields.io/badge/技能-150%2B-blue.svg)](./plugins)
[![Agents](https://img.shields.io/badge/代理-45%2B-purple.svg)](./plugins)

**🌐 语言:** [English](README.md) | [Italiano](./README_IT.md) | [中文](./README_CN.md) | [Español](./README_ES.md)

![](https://repository-images.githubusercontent.com/1080332870/5124e0d2-98f8-4486-9659-dde59a5ad251)

**一个模块化 AI 插件系统，为您的跨语言和跨框架开发工作流提供强大支持。**

[安装](#安装) • [快速开始](#快速开始) • [插件](#可用插件) • [文档](https://github.com/giuseppe-trisciuoglio/developer-kit/blob/main/README.md) • [更新日志](./CHANGELOG.md)

</div>

---

## 为什么选择 Developer Kit？

Developer Kit 是一个面向 Claude Code 的**模块化插件市场**，它教会 Claude 如何以可重复、高质量的方式执行开发任务。您无需获得通用的 AI 响应，而是获得针对您确切技术栈的领域专业知识。

- **🧩 模块化设计** — 只安装您需要的。Java 开发者？获取 `developer-kit-java`。全栈 TypeScript？添加 `developer-kit-typescript`。
- **🎯 领域专家** — 45+ 个专业代理，涵盖代码审查、重构、安全审计、架构设计和测试，支持 7+ 种语言。
- **📚 150+ 技能** — 从 Spring Boot CRUD 生成到 CloudFormation 模板的可复用能力，全部内置最佳实践。
- **🔄 多 CLI 支持** — 兼容 Claude Code、GitHub Copilot CLI、OpenCode CLI 和 Codex CLI。
- **⚡ 自动激活** — 基于路径的规则会在您打开相关文件时自动激活。无需配置。

---

## 安装

### 快速安装（推荐）

#### Claude Code

```bash
# 从市场安装
/plugin marketplace add giuseppe-trisciuoglio/developer-kit

# 或从本地目录安装
/plugin install /path/to/developer-kit
```

#### Claude Desktop

[在设置中启用技能](https://claude.ai/settings/capabilities) → 添加 `giuseppe-trisciuoglio/developer-kit`

#### 手动安装

```bash
# 克隆仓库
git clone https://github.com/giuseppe-trisciuoglio/developer-kit.git

# 通过 Makefile 安装（自动检测您的 CLI）
cd developer-kit
make install

# 或为特定 CLI 安装
make install-claude      # Claude Code
make install-opencode    # OpenCode CLI
make install-copilot     # GitHub Copilot CLI
make install-codex       # Codex CLI
```

---

## 快速开始

```bash
# 安装后，启动您的 CLI
claude

# 查看可用命令
/help

# 使用 Developer Kit 命令
/devkit.refactor

# 或启动需求工作流
/specs:brainstorm
```

### 提示示例

```
为 User 实体生成完整的 CRUD 模块，使用 NestJS 和 Drizzle ORM
审查此 Java Spring Boot 服务的安全问题
创建带有自动扩展的 ECS CloudFormation 模板
帮我把这个单体类重构为整洁架构
为此 TypeScript 服务生成单元测试，覆盖率达 100%
```

---

## 使用方法

Developer Kit 提供**四层**能力：

### 1. 技能
按需加载的可复用能力。示例：

```
[技能: spring-boot-crud-patterns 已激活]
```

技能自动为特定任务提供模式、模板和最佳实践。

### 2. 代理
用于复杂工作流的专业子代理：

```bash
# 通过自然语言调用
"以 Spring Boot 专家身份审查此代码"

# 或使用命令
/devkit.java.code-review
/devkit.typescript.code-review
```

### 3. 需求驱动开发 (SDD)
通过结构化工作流将想法转化为生产就绪代码：

![SDD 工作流](./docs/specs-life-cycle.png)

#### 阶段 1：需求创建

| 命令 | 使用时机 | 输出 |
|------|----------|------|
| `/specs:brainstorm` | 新功能、复杂需求 | 包含 9 个阶段的完整需求规格 |
| `/specs:quick-spec` | Bug 修复、小型增强 | 轻量级 4 阶段需求规格 |

需求规格保存在 `docs/specs/[id]/YYYY-MM-DD--feature-name.md`

#### 阶段 2：任务生成

| 命令 | 描述 |
|------|------|
| `/specs:spec-to-tasks` | 将需求规格转换为可执行的任务文件 |
| `/specs:task-manage` | 添加、拆分、更新或重新组织任务 |

任务生成在 `docs/specs/[id]/tasks/` 目录下，包含独立的任务文件。

#### 阶段 3：实现

| 命令 | 描述 |
|------|------|
| `/specs:task-implementation` | 特定任务的引导式实现 |
| `/specs:task-tdd` | 针对该任务的测试驱动开发方法 |

每个任务实现都会更新知识图谱以保留上下文。

#### 阶段 4：质量保证

| 命令 | 描述 |
|------|------|
| `/specs:task-review` | 验证任务是否符合需求规格和代码质量标准 |
| `/specs:code-cleanup` | 专业清理：移除调试日志、优化导入 |
| `/specs:spec-sync-with-code` | 将需求规格与实际实现同步 |

#### 附加工作流命令

| 命令 | 描述 |
|------|------|
| `/specs:spec-quality-check` | 需求规格的交互式质量评估 |
| `/specs:spec-sync-context` | 同步知识图谱、任务和代码库状态 |
| `/specs:ralph-loop` | 需求驱动开发的自动化循环 |
| `/devkit.refactor` | 通过架构分析重构现有代码 |
| `/devkit.github.create-pr` | 创建包含全面描述的 PR |

### 4. 规则
基于文件模式的自动激活规则：

```yaml
# 对 *.java 文件自动激活
globs: ["**/*.java"]
---
始终使用构造函数注入。永远不要使用带 @Autowired 的字段注入。
```

> **📋 规则安装说明**
>
> 插件不会自动将规则安装到项目中。要使用规则，你可以手动复制它们
> 或使用 Makefile 命令：
>
> ```bash
> # 复制特定插件的规则
> make copy-rules PLUGIN=developer-kit-java
>
> # 或手动从插件的 rules/ 文件夹复制 .md 文件
> mkdir -p .claude/rules
> cp plugins/developer-kit-[语言]/rules/*.md .claude/rules/
> ```
>
> 规则将根据每个文件头部定义的 `globs:` 模式自动激活。

---

## 可用插件

| 插件 | 语言/领域 | 组件 | 描述 |
|------|----------|------|------|
| `developer-kit-core` | 核心 | 6 代理、8 命令、4 技能 | 包含通用能力的基础插件（必需） |
| `developer-kit-specs` | 工作流 | 9 命令、2 技能 | 需求驱动开发（SDD）工作流 |
| `developer-kit-java` | Java | 9 代理、11 命令、51 技能、4 规则 | Spring Boot、LangChain4J、AWS SDK、GraalVM |
| `developer-kit-typescript` | TypeScript | 13 代理、3 命令、25 技能、17 规则 | NestJS、React、Next.js、Drizzle ORM、Monorepo |
| `developer-kit-python` | Python | 4 代理、4 规则 | Django、Flask、FastAPI、AWS Lambda |
| `developer-kit-php` | PHP | 5 代理、3 技能、4 规则 | WordPress、Sage、AWS Lambda |
| `developer-kit-aws` | AWS | 3 代理、19 技能 | CloudFormation、SAM、CLI、架构 |
| `developer-kit-ai` | AI/ML | 1 代理、3 技能、1 命令 | 提示工程、RAG、分块 |
| `developer-kit-devops` | DevOps | 2 代理 | Docker、GitHub Actions |
| `developer-kit-tools` | 工具 | 4 技能 | NotebookLM、Copilot CLI、Gemini、Codex |
| `github-spec-kit` | GitHub | 3 命令 | GitHub 需求规格集成 |

**总计：150+ 技能 | 45+ 代理 | 20+ 命令 | 45+ 规则**

---

## 插件架构

```
developer-kit/
├── plugins/
│   ├── developer-kit-core/          # 必需的基础
│   │   ├── agents/                  # 代理定义 (.md)
│   │   ├── commands/                # 斜杠命令 (.md)
│   │   ├── skills/                  # 可复用技能 (SKILL.md)
│   │   ├── rules/                   # 自动激活规则
│   │   └── .claude-plugin/
│   │       └── plugin.json          # 插件清单
│   ├── developer-kit-java/          # Java 生态系统
│   ├── developer-kit-typescript/    # TypeScript 生态系统
│   └── ...
├── .skills-validator-check/         # 验证系统
└── Makefile                         # 安装命令
```

每个插件都是自包含的，带有自己的清单、组件和依赖项。

---

## 配置

### 插件选择

只安装您需要的插件：

```bash
# 核心 + Java + AWS
make install-claude
# 然后启用：developer-kit-core、developer-kit-java、developer-kit-aws

# 全栈 TypeScript
# 启用：developer-kit-core、developer-kit-typescript、developer-kit-aws
```

### 规则自动激活

规则基于文件模式自动激活：

```yaml
---
globs: ["**/*.java"]
---
# 此规则对所有 Java 文件激活
- 使用构造函数注入
- 遵循命名约定
```

### LSP 集成

语言插件包含 LSP 服务器配置 (`.lsp.json`)：

| 语言 | 服务器 |
|------|--------|
| Java | jdtls |
| TypeScript | typescript-language-server |
| Python | pyright-langserver |
| PHP | intelephense |

---

## 语言支持矩阵

| 语言 | 技能 | 代理 | 命令 | 规则 | LSP |
|------|------|------|------|------|-----|
| Java/Spring Boot | 51 | 9 | 11 | 4 | ✅ |
| TypeScript/Node.js | 25 | 13 | 3 | 17 | ✅ |
| Python | 2 | 4 | 0 | 4 | ✅ |
| PHP/WordPress | 3 | 5 | 0 | 4 | ✅ |
| AWS/CloudFormation | 19 | 3 | 0 | 0 | ❌ |
| AI/ML | 3 | 1 | 1 | 0 | ❌ |

---

## 验证与质量

Developer Kit 包含全面的验证系统：

```bash
# 验证所有组件
python .skills-validator-check/validators/cli.py --all

# 安全扫描（MCP 合规性）
make security-scan

# 预提交钩子
.skills-validator-check/install-hooks.sh
```

---

## 生态系统

**已上架：**
- [context7](https://context7.com/giuseppe-trisciuoglio/developer-kit?tab=skills) — 技能市场
- [skills.sh](https://skills.sh/giuseppe-trisciuoglio/developer-kit) — AI 技能目录

**相关项目：**
- [Claude Code](https://claude.ai/code) — Anthropic 的 AI 驱动终端
- [OpenCode](https://github.com/opencode-ai/opencode) — 开源 AI 编码助手
- [GitHub Copilot CLI](https://github.com/github/copilot.vim) — AI 结对编程
- [Codex CLI](https://github.com/openai/codex) — OpenAI 的编码代理

---

## 贡献

我们欢迎贡献！请参阅 [CONTRIBUTING.md](./CONTRIBUTING.md) 了解：
- 添加新技能、代理和命令
- 插件开发指南
- 验证要求
- 分支策略和版本控制

## 安全

技能可以执行代码。部署前请审查所有自定义技能：

- ✅ 仅从可信来源安装
- ✅ 启用前审查 SKILL.md
- ✅ 先在非生产环境测试
- ✅ 发布前运行 `make security-scan`

每次 PR 都会通过 GitHub Actions 自动运行安全扫描。

---

## 许可证

[MIT 许可证](./LICENSE) — 开源且免费使用。

---

## 致谢

- **Claude Code** by Anthropic — 此插件系统扩展的基础
- **Qwen Code** — README 设计灵感来源
- **贡献者** — 感谢所有为技能和插件做出贡献的人

---

<div align="center">

**用 ❤️ 为使用 Claude Code 的开发者打造**

同时兼容 OpenCode、GitHub Copilot CLI 和 Codex

</div>
