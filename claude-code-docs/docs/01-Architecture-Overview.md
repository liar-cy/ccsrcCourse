[中文](01-架构总览.md)

# 01 Architecture Overview: How Claude Code Actually Runs

## First, some background: how the source leaked

In March 2026, someone noticed that the Claude Code client package published to npm shipped with sourcemap files. Sourcemaps exist for debugging — they record the mapping between bundled code and the original source. They should be excluded at publish time, but Anthropic's build pipeline missed that step.

Someone used the sourcemaps to reconstruct the complete TypeScript source: 515,000 lines across 2,766 files, the entire logic of the Claude Code client laid bare.

**Note that only the client-side code leaked.** Claude Code uses a textbook client-server split. The client runs in your terminal and handles user interaction, tool execution, permission management, and context assembly. The server is Anthropic's API, which handles model inference. The model itself and the server-side logic did not leak.

The client code alone is valuable enough, because the competitive edge of an agent product does not live in the model call. It lives in **how you release the model's capability safely, efficiently, and reliably**. That is the domain of harness engineering, and the client code is a complete harness implementation.

## What Claude Code is

If you have never used it, thirty seconds of context.

Claude Code is Anthropic's official AI programming assistant, positioned as a coding agent, running in your terminal. You type `claude` and land in a conversational interface. You ask in natural language for it to write code, edit code, read files, search the codebase, run commands, do research. It decides on its own which tool to use, which file to read, which command to run — like a colleague sitting next to you pair programming.

Unlike the ChatGPT or Claude web chat box, Claude Code **operates your machine directly**. It reads and writes your filesystem, executes bash commands, and opens a browser to fetch pages.

As a product its competitors are Cursor, Windsurf, and GitHub Copilot CLI. As an architecture it is a standard **ReAct agent**, and the core loop is: think → call a tool → observe the result → keep thinking.

## Tech stack

| Layer | Technology | Why this one |
|---|---|---|
| Runtime | Bun 1.3.11+ | Faster than Node.js, native TypeScript, bundler built in |
| Language | TypeScript 6.0.2 | Type safety — 515K lines is unmaintainable without a type system |
| Terminal UI | React 19.2.4 + ink | Renders the terminal interface with the React component model |
| CLI framework | Commander.js 14.0.0 | Mature command-line argument parsing |
| API | Anthropic SDK | Calls Claude models; also supports AWS Bedrock, Azure, and Vertex |
| Code quality | Biome 2.4.10 | Lint and format in one, faster than ESLint plus Prettier |

## Overall architecture

The whole picture first, then layer by layer.


```
┌──────────────────────────────────────────────────────────┐
│                 User types in the terminal                │
└───────────────────────┬──────────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────────┐
│  CLI entry layer                                          │
│  cli.tsx → init.ts → main.tsx                             │
│  Parses argv, initializes config, starts the REPL or      │
│  executes a single command                                │
└───────────────────────┬──────────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────────┐
│  Session layer                                            │
│  QueryEngine.ts (1,300 lines)                             │
│  Owns the conversation lifecycle, message history, and    │
│  auto-compaction scheduling. Effectively a session-level  │
│  state machine tracking 20+ config parameters             │
└───────────────────────┬──────────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────────┐
│  Agent core loop                                          │
│  query.ts (1,700 lines)                                   │
│  The full ReAct implementation:                           │
│  prefetch → build prompt → call API → run tools →         │
│  compact → continue?                                      │
│  This is the heart of the system                          │
└───────────┬───────────────────────┬──────────────────────┘
            │                       │
┌───────────▼──────────┐ ┌──────────▼───────────────────┐
│  Permission system    │ │  Tool execution layer         │
│  6,300 lines/25 files │ │  40+ tools                    │
│  3 modes + 42 rules   │ │  Bash / File / Web / Agent    │
│  ML classifier + jail │ │  Skill / MCP / Task           │
└──────────────────────┘ └───────────────────────────────┘
            │                       │
            └───────────┬───────────┘
                        │
┌───────────────────────▼──────────────────────────────────┐
│  Context and memory layer                                 │
│  CLAUDE.md five-layer loading / MEMORY.md / Session Memory│
│  Git status injection / Skill list / permission rules     │
│  Three-tier compaction: micro / Session Memory / full     │
└───────────────────────┬──────────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────────┐
│  API client layer                                         │
│  claude.ts (800+ lines)                                   │
│  Calls the Anthropic API with streaming output            │
│  Model fallback chain: Opus → Sonnet → Small              │
│  Retry logic, prompt cache optimization, multi-backend    │
└──────────────────────────────────────────────────────────┘
```

### How this differs from a general agent framework

Most agent frameworks on the market — LangChain, AutoGen, CrewAI — are **libraries**. They hand you an API and you call it from your own code to build an agent.

Claude Code is **a finished product**. Terminal UI, permission management, context engineering, message compaction: all implemented in-house, with no agent framework underneath.

That means the code contains a lot of things an agent framework will never tell you:

- how to do real-time streaming rendering inside a terminal
- how to degrade gracefully when the user's network drops
- how to compact automatically when the context is nearly full
- how to prefetch in the background without the user noticing
- how to maximize prompt cache hit rate to hold cost down

**Those engineering details are the most valuable part of this source.**

## The complete journey of one request


What happens between typing a line in the terminal and seeing the agent reply?

### Step 1: capture the input

You type and hit enter. The REPL layer classifies what kind of input it is:

- starts with `!` → **execute the shell command directly**, bypassing the agent. `! ls`, `! git status`. It is a shortcut so you can run a command without leaving Claude Code; output goes straight to the terminal
- starts with `/` → a **slash command** such as `/clear`, `/compact`, `/help`. These are built-in shortcuts the client handles itself
- otherwise → **natural language**, which enters the agent loop and goes to the model

### Step 2: assemble the context

Before calling the API the system assembles a complete context. That context determines what the model sees, knows, and can do.

**The system prompt is concatenated from:**

1. built-in agent behavior rules telling the model it is Claude Code, that it can read and write files and execute commands, and how it should interact with the user
2. the user's CLAUDE.md memory files, loaded across five priority layers from global to project to local
3. a snapshot of the current Git repository: branch, recent commits, which files changed
4. permission rules: which tools may run automatically and which need confirmation
5. the Skill list: the extension capabilities currently available

All of it concatenated is the model's system prompt. This process is **context engineering**, and a later chapter covers it in detail.

### Step 3: streaming API call

With the request assembled, a streaming API call goes out through the Anthropic SDK. The model returns tokens one at a time and the client renders each one to the terminal as it arrives, so the user watches the model "type."

If the model decides to call a tool, it emits a `tool_use` block in the response carrying the tool name and arguments. To read a file, it emits:

```json
{
  "type": "tool_use",
  "name": "Read",
  "input": { "file_path": "/src/main.ts", "limit": 100 }
}
```

### Step 4: permission check and tool execution

Once `tool_use` arrives, the permission check runs first:

- hardcoded rules: 42 dangerous commands rejected outright, without asking
- ML classifier: judges whether this command is safe
- user rules: matched against the user's configured allow and deny lists
- confirmation prompt: when none of the above match, ask the user

After the check passes the tool runs, and multiple tool calls can run in parallel.

When execution finishes, the tool result is appended to the message history as `tool_result`.

### Step 5: compaction check

The total token count of the message history is checked. If it approaches the context window limit, compaction triggers:

1. **Micro-compact**: clear out old tool outputs, the content whose relevance decays fastest
2. **Session Memory**: settle key information into memory files to free context space
3. **Full compact**: fork a separate agent to summarize everything, condensing the whole conversation history into one summary

### Step 6: continue or stop

Look at the `stop_reason` the API returned:

- `tool_use`: the model wants another tool, so go back to step 3 and loop
- `end_turn`: the model considers the task complete, so stop
- `max_tokens`: output hit the ceiling and may need to continue

A complex task can loop dozens of times. Ask Claude Code to refactor a module and it may read several files to understand the current state, edit the code, run the tests, find a failure, edit again, run again — each tool call is one turn of the loop.

## Core file reference

If you want to read the source yourself, this table will orient you:

| File | Lines | What it does | When to read it |
|---|---|---|---|
| `src/query.ts` | 1,700 | Agent core loop, six-phase streaming orchestration | Understanding how the agent runs |
| `src/QueryEngine.ts` | 1,300 | Session state machine, 20+ config parameters | Understanding session management and config |
| `src/main.tsx` | 5,000+ | CLI entry, everything crammed in | Understanding the startup path |
| `src/context.ts` | 200+ | Git status injection, context assembly | Understanding context engineering |
| `src/utils/claudemd.ts` | 1,400+ | CLAUDE.md five-layer loading, @include | Understanding the memory system |
| `src/services/compact/` | 26 files | Three-tier message compaction | Understanding long-conversation management |
| `src/utils/permissions/` | 6,300+ | Three-mode permission system | Understanding the security design |
| `src/services/api/claude.ts` | 800+ | API client, retry, model fallback | Understanding the API layer |
| `src/tools.ts` | 300+ | Tool registry, feature flag control | Finding out which tools exist |
| `src/services/mcp/` | 12,000+ | MCP protocol integration | Understanding external tool integration |

## Side by side with other agents


| Dimension | Claude Code | Cursor | LangChain Agent | AutoGen |
|---|---|---|---|---|
| Form | Terminal CLI | IDE plugin | Python library | Python framework |
| Agent loop | In-house ReAct + AsyncGenerator | Not public | ReAct / Plan-and-Execute | GroupChat + Planner |
| Permissions | 6,300 lines, 3 modes + ML classifier | IDE-level sandbox | Essentially none | Essentially none |
| Context management | Three-tier compaction + prefetch cache + prompt cache optimization | Not public | Simple token truncation | None |
| Memory | Five-layer CLAUDE.md + MEMORY.md + Session Memory | Project-level index | Manual configuration | ConversableAgent memory |
| Tools | 40+ built in, plus Skill and MCP | Built in plus plugins | Register your own | Register your own |
| Codebase size | 515K lines | Not public | ~50K lines | ~30K lines |

Claude Code's engineering complexity far exceeds that of the open-source agent frameworks. An agent product facing real users has to handle one to two orders of magnitude more edge cases than an agent framework does.

## Key numbers


| Metric | Value |
|---|---|
| Codebase | 515,498 lines of TypeScript/TSX |
| Files | 2,766 |
| Build output | 25.89 MB, 5,344 modules |
| Built-in tools | 40+ |
| Feature flags | 82 |
| Permission rules | 42 hardcoded dangerous patterns |
| Compaction threshold | Context window − 13,000 tokens |
| npm dependencies | 583 packages |

## Was it written by AI?

Yes. All 20 commits come from `claude-code-best`, and three of them carry `Co-Authored-By: Claude Opus 4.6`. 515,000 lines compiled with zero errors on the first try. [02-Value-Debate](02-Value-Debate.md) has the details.

## Next

You now have a whole-system picture of Claude Code. From here we go module by module.

Next up, [02-Value-Debate](02-Value-Debate.md) asks whether this code is actually worth anything, and where the real moat in harness engineering lies.
