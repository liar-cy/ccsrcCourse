# Claude Code 源码课程生成规范

## 任务定位

本文件约束后续在本仓库工作的 Agent。当前阶段的目标不是修改、重构或重新发布 Claude Code，而是基于 `@anthropic-ai/claude-code` 2.1.88 发布包的 source map，生成适合中文学习者的源码解析课程。

默认读者：

- 能阅读基础 Python；
- 对 Agent 产品和 Claude Code 感兴趣；
- 不要求熟悉 TypeScript、React、Ink 或 Rust；
- 更需要架构、运行流程和工程取舍，而不是逐行翻译源码。

项目不是 Rust 工程。若用户提到“不熟悉 Rust”，应温和说明当前源码是 TypeScript/TSX，并继续使用 Python 对照降低语言门槛。不得为了迎合先入印象而虚构 Rust crate、trait 或 Tokio 运行时。

## 适用范围与优先级

1. 用户在当前任务中的明确要求优先于本文件。
2. 根目录 `README.md` 定义 P00–P13 分区、学习顺序和术语，本文件定义课程生成方式。
3. 子目录若以后出现更具体的 `AGENTS.md`，只覆盖其目录范围内的细节；事实与证据规则不得降低。
4. 未被要求生成课程时，不要提前批量创建课程文件。

## 仓库事实

- 版本：`2.1.88`，以 `claude-code-sourcemap/package/package.json` 和 `cli.js --version` 为准。
- 主要证据：`claude-code-sourcemap/package/cli.js.map` 中的 `sources`/`sourcesContent`。
- 可读源码：运行提取脚本后位于 `claude-code-sourcemap/restored-src/src/`。
- 自有源码范围：source path 以 `../src/` 开头的文件。
- 非自有源码：`../node_modules/`、vendor 二进制、第三方生成代码，默认排除课程主线。
- 已有解读：`claude-code-docs/docs/`，只能作为二手参考，不能代替源码核验。
- 快照不包含完整官方 monorepo、服务端推理实现或可靠的完整测试/构建环境。

如果 `restored-src/` 尚未生成，可以直接解析 `cli.js.map`，或先执行仓库已有提取脚本。不要把临时分析产物、依赖安装目录或解压副本提交到项目中。

## 固定课程分区

所有课程必须归入以下一个主分区，文件名建议使用 `Pxx-yy-主题.md`：

| 分区 | 名称 | 主范围 |
|---|---|---|
| P00 | 快照与阅读方法 | source map、发布包、提取方式、证据边界 |
| P01 | 启动、初始化与运行模式 | `entrypoints/`、`main.tsx`、`bootstrap/`、CLI handlers |
| P02 | 终端 UI 与输入系统 | `screens/REPL.tsx`、`components/`、`ink/`、`hooks/`、键位与 vim |
| P03 | 消息模型、会话与恢复 | message types、`messages.ts`、`sessionStorage.ts`、history/state |
| P04 | Agent 核心循环 | `query.ts`、`query/`、`QueryEngine.ts`、输入处理 |
| P05 | 模型 API 与流式协议 | `services/api/`、model、tokens、cost |
| P06 | 上下文、Prompt、记忆与压缩 | prompts、context、attachments、CLAUDE.md、memory、compact |
| P07 | 工具抽象与执行流水线 | `Tool.ts`、`tools.ts`、`tools/`、`services/tools/` |
| P08 | 权限、安全与沙箱 | permissions、sandbox、shell security、permission UI/hooks |
| P09 | 命令、配置与 Hook | commands、settings/config、hooks lifecycle |
| P10 | MCP、Skill 与 Plugin 扩展 | MCP client/tools、skills、plugins |
| P11 | 子 Agent、任务与多 Agent | AgentTool、tasks、forkedAgent、swarm、coordinator、mailbox |
| P12 | 远程、Bridge 与外部客户端 | remote、bridge、transports、structured IO、SDK schemas |
| P13 | 认证、平台与可观测性 | auth/OAuth、analytics/telemetry、`utils/platform.ts`、native、migrations |

跨区文件按“本课解释的责任”归属。例如 `BashTool` 的执行契约归 P07，危险命令判定归 P08；不要复制两篇近似课程。

## 接到课程任务后的工作流程

### 1. 明确课程边界

- 确认分区编号、课题、读者前置和期望深度。
- 若用户只给分区名，自主选择一条最小完整主流程，不要停下来索要函数清单。
- 列出本课明确不讲的相邻主题，防止范围膨胀。

### 2. 建立源码证据集

- 从入口调用点开始，沿 import、函数调用、类型引用追踪到终点。
- 至少核对一个正常路径、一个失败/取消路径，以及相关的持久化或清理动作。
- 记录 feature flag、环境变量、运行模式和 provider 差异。
- 超大文件只读取相关区段，不能凭文件名推断职责。
- 用 `rg`/`rg --files` 搜索；生成目录统计时必须把 `../src/` 与 `../node_modules/` 分开。

### 3. 先画模型，再写文字

写作前先在草稿中回答：

- 输入是什么？
- 谁拥有状态？
- 核心状态怎样变化？
- 输出或事件是什么？
- 何时继续、停止、重试、压缩或回滚？
- 权限与信任边界在哪里？

只有三步以上的时序、三方以上的依赖或复杂状态切换才使用 Mermaid。简单内容用短列表或表格。

### 4. 用 Python 降低语法门槛

- 课程主体先解释语言无关的机制，再解释 TypeScript 落点。
- 若 TypeScript 片段包含泛型、联合类型、AsyncGenerator、React hook、高阶函数或复杂异步控制，紧邻给出 Python 对照。
- Python 示例应可独立理解，优先使用标准库：`dataclasses`、`typing`、`asyncio`、`enum`。
- 对照实现保留关键控制流和状态，不复制 UI 细节、遥测字段和所有错误分支。
- 明确标注“教学简化版”，不得声称 Python 与 Bun/React 运行时完全等价。

### 5. 完成验证

- 回查每个事实性结论是否能指向源码文件和符号。
- 检查路径是否真实存在于 `sources`；feature-gated 引用可能只在 source map 中存在、未进入公共 bundle，必须说明。
- 检查课程是否把客户端行为误写成模型或服务端行为。
- 检查是否暴露密钥、内部 token、个人路径，或给出权限绕过步骤。
- 检查 Python 示例能否通过基本语法运行；若只是伪代码要明确标注。

## 单课标准模板

除非用户另有要求，每课使用以下结构。不要为了填模板制造空章节。

```markdown
# Pxx-yy 课程标题

> 一句话回答本课解决什么问题。

## 学习目标
## 前置知识与范围
## 在整体架构中的位置
## 先用 Python 建立最小模型
## Claude Code 的真实实现流程
## 关键数据结构与状态变化
## 源码锚点
## 失败路径、安全边界与设计取舍
## 动手练习
## 小结与检查题
## 版本与证据说明
```

“源码锚点”建议用表格：

| 文件/符号 | 在流程中的职责 | 建议关注 |
|---|---|---|
| `src/example.ts: symbolName` | 一句话职责 | 状态、分支或设计点 |

行号只作为当前快照的辅助定位，不作为长期标识；必须同时写符号名，因为后续版本行号会漂移。

## 写作标准

### 必须做到

- 使用简体中文，首次出现的英文术语给出中文解释。
- 先给结论和心智模型，再给源码证据。
- 每一节围绕一个问题，不按文件顺序机械复述。
- 明确区分“代码事实”“合理推断”“教学简化”“已有文档观点”。
- 解释状态所有权、输入输出、时序、异常与取消，而不只讲 happy path。
- TypeScript 摘录保持最小，通常单段不超过 20 行；超过时改为流程图或伪代码。
- Python 代码命名尽量贴近业务概念，不保留混淆后的 bundle 符号。
- 链接使用仓库相对路径；引用还原源码时注明需先生成 `restored-src/`。
- 课程结尾列出 3–5 个可自检问题，答案能由本课推出。

### 不要这样做

- 不要逐行翻译 1,000 行以上的大文件。
- 不要大段复制版权源码、system prompt、危险规则全集或内部文案。
- 不要把 React 组件树当成浏览器 DOM；Ink 输出目标是终端。
- 不要把 `QueryEngine` 说成当前交互 REPL 的唯一会话引擎；2.1.88 中 REPL 仍直接调用 `query()`。
- 不要把 `stop_reason === 'tool_use'` 当成唯一继续依据；源码注释明确指出它并不总可靠。
- 不要因为存在 feature-gated 源文件就断言功能已发布。
- 不要把客户端的 prompt、编排或权限逻辑说成 Anthropic 服务端实现。
- 不要用“显然”“简单地”“只是”跳过关键工程细节。
- 不要生成与当前课程无关的重构、补丁或可执行攻击示例。

## 证据等级

课程的重要结论按以下等级标注或在“版本与证据说明”中汇总：

| 等级 | 含义 | 可用表述 |
|---|---|---|
| A | 当前 `../src/` 源码与公共 `cli.js` 均能验证 | “2.1.88 公共构建会……” |
| B | source map 自有源码可验证，但路径受 build-time/runtime flag 控制 | “源码包含……；当前公共构建是否启用需再核对” |
| C | 仅已有文章、注释、命名或不完整上下文支持 | “推测/注释表明……，不能据此确认上线行为” |

涉及版本、数量、阈值、默认值、权限模式、危险规则条数、配置优先级等易漂移事实时，必须给出快照版本和证据等级。不要无核验继承旧文档中的数字。

## Python 对照规则

### AsyncGenerator

TypeScript 的流式 Agent 循环优先映射成：

```python
from collections.abc import AsyncIterator

async def agent_loop(state: "State") -> AsyncIterator["Event"]:
    while True:
        async for event in call_model(state.messages):
            yield event
        if state.should_stop:
            return
        await execute_requested_tools(state)
```

必须解释：`yield` 的价值是把模型增量、工具进度和最终消息统一成事件流，而不只是“异步语法”。

### Discriminated Union

用带类型字段的 dataclass 表达，不必模拟 TypeScript 所有类型技巧：

```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class ToolUse:
    type: Literal["tool_use"]
    name: str
    input: dict[str, object]
```

### React/Ink

先用“状态 → UI 描述 → 终端渲染”的单向数据流解释。Python 可用普通状态机或 Textual/Rich 类比，但除非用户要求，不新增第三方框架依赖。

### 权限与取消

权限结果使用明确枚举/联合，不用裸布尔值；取消用 `asyncio.Event` 或 `CancelledError` 类比，并说明真实实现使用 `AbortController`。

## 分区专项要求

### P01 / P02

- 区分 bootstrap、初始化、命令解析和真正挂载 UI 的时点。
- 比较交互与非交互模式，不要只讲默认 TTY 路径。

### P03 / P04

- 明确内部 `Message`、API message、SDK event、UI message 不是同一个层次。
- 画出 tool_use/tool_result 配对、compact boundary 和 interruption 的位置。
- 比较 `REPL.tsx → query()` 与 `QueryEngine.submitMessage() → query()` 两条路径。

### P05 / P06

- 区分 token 预算、上下文窗口、输出 token、费用预算。
- 压缩课程至少比较 microcompact、autocompact/full compact、session memory 的触发与产物。
- system prompt、user context、system context、attachment、CLAUDE.md 不可混为一类。

### P07 / P08

- 工具调用固定按“发现/注册 → schema → 输入校验 → 权限 → 执行 → 进度 → 结果”讲。
- 权限固定按“规则来源 → 合并 → 匹配优先级 → 用户交互 → 持久化”讲。
- Bash/PowerShell 内容只做防御性学习；危险命令示例使用无破坏性的占位命令。

### P09 / P10

- 明确 slash command、Skill、Plugin、MCP tool、内置 Tool 的差别和组合关系。
- MCP 需区分配置、连接/传输、能力发现、OAuth、工具适配、权限治理。

### P11 / P12

- 说明父子 Agent 的上下文继承、消息隔离、取消、结果回传和 transcript 关系。
- 并发只在源码证据支持的情况下描述；不要把所有多工具调用都说成并行。
- 远程课程明确本地信任边界、网络传输边界和权限桥接。

### P13

- 遥测和 feature flag 只讲架构与观测目的，不收集或展示真实用户标识。
- provider、认证和策略必须区分 Anthropic API、Bedrock、Vertex、Foundry 等路径。

## 文件与变更约束

- 生成课程前先查看工作区状态；已有变更视为用户所有，不覆盖、不回滚。
- 除非用户明确要求，不修改 `claude-code-sourcemap/package/`、还原源码或已有 `claude-code-docs/`。
- 不提交 `node_modules/`、临时提取目录、运行日志、凭据、缓存或大体积生成物。
- 创建新课程时优先放到用户指定目录；若未指定，先提出建议目录，不要在一次任务里自动生成全部 P00–P13。
- 修改文档后检查相对链接、Markdown 表格、Mermaid 语法、代码块语言和中文标点。

## 单课验收清单

提交课程前逐项确认：

- [ ] 课程已归入一个 P00–P13 主分区。
- [ ] 说明了本课范围与不讲内容。
- [ ] 至少追踪一条端到端主流程。
- [ ] 至少覆盖一个失败、取消或安全分支。
- [ ] 关键结论能定位到真实源码文件与符号。
- [ ] 区分当前公共行为、feature-gated 源码与推断。
- [ ] 没有把 `node_modules` 当作 Claude Code 自有实现。
- [ ] 没有把客户端逻辑误写成服务端或模型内部逻辑。
- [ ] TypeScript 片段克制，复杂语法已有 Python 对照。
- [ ] Python 示例是可运行代码或已标注伪代码。
- [ ] 没有大段复制版权代码、prompt 或危险规则。
- [ ] 图表确实降低理解难度，且与正文一致。
- [ ] 包含练习、自检问题和版本/证据说明。

## 完成汇报格式

Agent 完成课程任务后，用简短中文汇报：

1. 创建或更新了哪些文件；
2. 本课覆盖的主调用链；
3. 使用了哪些 Python 对照；
4. 哪些结论受 feature flag、快照缺失或版本漂移限制；
5. 做了哪些验证。

不要在汇报中声称“理解了全部 51 万行源码”。应准确说明实际追踪的文件、符号和路径。
