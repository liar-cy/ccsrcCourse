# Changelog

All notable changes to this documentation set are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/) adapted for documentation:

- **MAJOR** — a chapter's conclusion changed, or chapters were added/removed
- **MINOR** — substantive content added to an existing chapter
- **PATCH** — corrections, link fixes, translation and wording repairs

## [Unreleased]

## [1.1.0] — 2026-08-11

### Fixed

- All 56 chapter cross-links resolved to `docs/<file>.md` from inside `docs/`, which 404'd in GitHub's file view and only worked on the docsify site. They are now same-directory relative and correct in both contexts. ([#1](https://github.com/anneheartrecord/claude-code-docs/pull/1))
- `docs/12-Agent-Security-Design.md` linked to `13-啃完51万行源码的发现与Claude的封号机制.md`, a filename that no longer exists after chapter 13 was renamed. Dead in every context.
- The Chinese chapter 12 pointed at chapter 13 under its old title.
- `_sidebar.md` and `_home.md` now use root-absolute paths, required once `relativePath` is enabled.

### Added

- `LICENSE` — MIT, matching the declaration the READMEs have carried since the first release, plus a scope note clarifying that no Claude Code source is redistributed here.
- `CONTRIBUTING.md` / `CONTRIBUTING_EN.md` — what corrections are wanted, the evidence bar for a factual correction, and the link conventions.
- `CODE_OF_CONDUCT.md` — Contributor Covenant 2.1.
- `scripts/check_links.py` — validates every local Markdown and image link and enforces the per-context link convention.
- `scripts/check_bilingual.py` — flags chapters that exist in only one language or whose two sides have drifted apart in size.
- GitHub Actions workflow running both checks on every push and pull request.
- Issue templates for chapter corrections, version drift, and new chapter proposals; a pull request template.
- Version coverage table in both READMEs, recording which source snapshot the analysis was verified against.
- English chapter 01 expanded from a summary to full parity with the Chinese: source-leak background, what Claude Code is, how it differs from an agent framework, the six-step request journey, the industry comparison table, and the key-numbers table. It was previously 5.2 KB against 15 KB of Chinese.

### Changed

- docsify `relativePath` switched to `true` so a single link form works on the published site and on GitHub.
- `.idea/` removed from version control and added to `.gitignore`.

## [1.0.0] — 2026-04-24

### Added

- 13 chapters of teardown analysis in Chinese and English, covering architecture, the agent loop, context engineering, the compaction system, permissions, memory, tools and skills, MCP integration, the feature-flag roadmap, code review in the AI coding era, agent security design, and closing findings.
- 59 hand-drawn illustrations across all 13 chapters.
- docsify site published to GitHub Pages.

[Unreleased]: https://github.com/anneheartrecord/claude-code-docs/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/anneheartrecord/claude-code-docs/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/anneheartrecord/claude-code-docs/releases/tag/v1.0.0
