[中文](./CONTRIBUTING.md)

# Contributing

This is a technical analysis repository. The most valuable contribution is not adding content — it is **telling me where I got it wrong**. A factual error in a source-code teardown gets quoted downstream as a conclusion.

## The three contributions I want most

| Type | What it means | Where it goes |
|---|---|---|
| **Factual correction** | A passage contradicts actual source behavior, a number is wrong, a module's responsibility is misdescribed | Open an issue using the `Chapter correction` template |
| **Version drift** | Upstream changed; a chapter now describes a mechanism that no longer exists | Open an issue using the `Version drift` template |
| **Translation & wording** | The Chinese and English versions disagree, a translation reads awkwardly, terminology is inconsistent | Send a PR directly |

Not accepted: bulk typo-only PRs (open one issue instead — faster for both of us), AI-generated whole new chapters, topics unrelated to agent architecture.

## Corrections must carry evidence

This is a hard requirement. "I think this is wrong" cannot be acted on and will be sent back for detail. A usable correction includes at least:

1. **Chapter and location** — which document, which section, quote the original sentence.
2. **What you believe the correct description is.**
3. **Evidence** — a source file path plus symbol name, reproducible steps that show the behavior, or a link to official documentation. Any one of the three.

## PR workflow

```bash
git checkout -b fix/<chapter>-<short-description>
# after editing, self-check
python3 scripts/check_links.py
git commit -m "fix(docs): <description>"
```

- Use Conventional Commits (`fix` / `docs` / `feat` / `chore`).
- **Keep both languages in sync.** If you change factual content in `docs/04-Context-Engineering.md`, update `docs/04-上下文工程.md` too, and vice versa. Single-language factual PRs will be sent back.
- Run `python3 scripts/check_links.py` before pushing.
- One PR, one concern.

## How to write links

The site runs docsify with `relativePath: true`, so:

- Cross-links **inside** `docs/` use same-directory relative paths: ``[04-Context Engineering](04-Context-Engineering.md)``
- `_sidebar.md` and `_home.md` use **root-absolute** paths: ``[01-Architecture Overview](/docs/01-Architecture-Overview.md)``
- `README.md` is read on GitHub, so it uses `./docs/xxx.md`

Getting this wrong produces links that work on the site but 404 on GitHub, or the reverse. `scripts/check_links.py` catches it.

## Maintenance cadence

- Issues get a first response **within 7 days** (triaged, or sent back for evidence).
- Factual corrections are the highest priority.
- When upstream changes something that invalidates a chapter's conclusion, a tracking issue is opened; once merged, a tag and release follow. See [CHANGELOG.md](./CHANGELOG.md).

## Code of Conduct

By participating you agree to the [Code of Conduct](./CODE_OF_CONDUCT.md).
