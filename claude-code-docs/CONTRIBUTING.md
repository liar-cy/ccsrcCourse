[English](./CONTRIBUTING_EN.md)

# 贡献指南

这是一个技术分析文档仓库。最有价值的贡献不是「加内容」，而是**指出哪里写错了**——源码解读一旦有事实性错误，会被读者当成结论直接引用。

## 我最需要的三类贡献

| 类型 | 说明 | 走哪条路 |
|---|---|---|
| **事实纠错** | 某段描述与源码实际行为不符、数字有误、模块职责搞反了 | 开 issue，用 `章节纠错` 模板 |
| **版本漂移** | 上游已变更，某章描述的机制已过时 | 开 issue，用 `版本漂移` 模板 |
| **翻译与表述** | 中英双语版本内容不一致、译文别扭、术语不统一 | 直接提 PR |

不接受的：纯 typo 批量 PR（直接开 issue 我一次改完更快）、AI 生成的整章新内容、与 Agent 架构无关的话题。

## 事实纠错必须带证据

这是硬性要求。只说「我觉得不对」无法处理，issue 会被要求补充后才处理。一条合格的纠错至少包含：

1. **章节与位置**：哪一篇、哪一节、原文怎么写的（引用原句）。
2. **你认为的正确描述**。
3. **证据**：源码文件路径 + 符号名 / 行为可复现的操作步骤 / 官方文档链接，三者任一。

## PR 流程

```bash
git checkout -b fix/<章节号>-<简述>
# 改完后自检
python3 scripts/check_links.py
git commit -m "fix(docs): <说明>"
```

- commit message 用 Conventional Commit（`fix` / `docs` / `feat` / `chore`）。
- **中英双语同步**：改了 `docs/04-上下文工程.md` 的事实性内容，就要同步改 `docs/04-Context-Engineering.md`，反之亦然。只改一边的 PR 我会打回。
- 改完跑一次 `python3 scripts/check_links.py`，确保没有引入坏链。
- 一个 PR 只解决一件事。

## 链接怎么写

站点用 docsify 且开了 `relativePath: true`，所以：

- `docs/` **内部**互链用同目录相对路径：``[04-上下文工程](04-上下文工程.md)``
- `_sidebar.md`、`_home.md` 用**根绝对路径**：``[01-架构总览](/docs/01-架构总览.md)``
- `README.md` 是给 GitHub 看的，用 `./docs/xxx.md`

写错会导致「站点能跳、GitHub 404」或反过来。`scripts/check_links.py` 会拦住。

## 维护节奏

- issue 我会在 **7 天内**给出首次回应（标记分类或要求补证据）。
- 事实纠错类 issue 优先级最高。
- 每次上游出现影响章节结论的重大变更，会开一个 tracking issue，合并后打 tag 发 release，见 [CHANGELOG.md](./CHANGELOG.md)。

## 行为准则

参与本项目即表示你同意遵守 [Code of Conduct](./CODE_OF_CONDUCT.md)。
