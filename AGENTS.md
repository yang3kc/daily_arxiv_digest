# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository. (CLAUDE.md includes it via `@AGENTS.md`.)

## Project Overview

Daily arXiv Digest is a headless CLI tool that fetches papers from arXiv RSS feeds, uses an LLM to rate their relevance against user-defined topics, and writes a daily digest to `digests/YYYY-MM-DD/` as both markdown (for humans) and JSON (for agents). It is designed to run unattended in a cron job or be invoked by another agent.

## Commands

### Development and Running
- `make run` or `make all` - Generate today's digest
- `uv run python main.py` - Direct command (flags: `--config`, `--date`, `--force`)
- `uv run python main.py --rethreshold X` - Rebuild digest.md/digest.json from saved scores.json at threshold X (no fetch/re-score; TL;DRs cached in tldrs.json)
- `uv sync` - Install/update dependencies

### Testing
- `uv run python test_llm.py` - Basic integration check: fetches one feed, scores one paper, writes one TL;DR

## Architecture

### Core Components
- `main.py` - CLI entry point (argparse); loads `.env`, handles the already-exists/`--force` check
- `src/digest.py` - Pipeline orchestration: fetch → score → select → TL;DR → render/write
- `src/rss.py` - ArxivRSS class handles fetching papers from arXiv RSS feeds
- `src/llm.py` - Provider registry (`PROVIDERS`), `create_client()`, and LLMPaperReader (relevance scoring + TL;DR generation)
- `src/logger.py` - JSONL activity logging to `logs/activity.jsonl`; inspect with `check_log.py`

### Key Design Patterns
- **Idempotent runs**: Output is keyed by date; if `digests/<date>/digest.json` exists the run exits cleanly (exit 0) without API calls, unless `--force`
- **Multi-provider via one code path**: OpenAI, Anthropic, and OpenRouter are all accessed through the OpenAI SDK (base_url override + per-provider API key env var); structured output via `chat.completions.parse` with Pydantic models
- **Concurrent Processing**: ThreadPoolExecutor (50 workers by default) for both scoring and TL;DR phases
- **Error Resilience**: Retry logic with graceful fallbacks — failed scoring returns neutral (0.0) judgements, failed TL;DRs return empty strings, so a batch never aborts
- **Configuration-Driven**: All settings (topics, arXiv subjects, provider/model, threshold, output dir) are in `config.json`

### Data Flow
1. Fetch papers from configured arXiv RSS feeds (`arxiv_subjects` in config.json), deduplicate by id
2. Concurrently score every paper against every topic
3. Select judgements with relevance ≥ `relevance_threshold`
4. Generate one TL;DR per selected paper (a paper can match several topics)
5. Write `digest.json` (selected papers), `digest.md` (rendered digest grouped by topic), and `scores.json` (raw scores for every fetched paper, for re-filtering at any threshold without re-scoring)

### Output Contract
`digest.json` top-level: `date`, `generated_at`, `provider`, `model`, `relevance_threshold`, `arxiv_subjects`, `topics`, `stats {papers_fetched, papers_selected}`, `papers[]`.
Each paper: `id`, `title`, `authors[]`, `url`, `abstract`, `tldr`, `matched_topics[] {topic, relevance, reason}` (only judgements ≥ threshold).
`scores.json`: same metadata (no threshold/stats) with `papers[]` covering EVERY fetched paper; each has `judgements[] {topic, relevance, reason}` for ALL topics.
`tldrs.json`: cache of `{paper_id: tldr}` accumulated across runs/rethresholds of the same date.
Papers are sorted by max relevance, descending, in both files. On days with no arXiv announcements empty files are still written.

## Configuration

### Environment Requirements
- API key env var matching `llm_provider`: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `OPENROUTER_API_KEY`
- Keys can live in a local `.env` file (gitignored, loaded via python-dotenv at entry points; template in `.env.example`); shell env vars take precedence
- Python 3.12+ required
- Uses `uv` package manager

### Key Configuration Files
- `config.json` - arXiv subjects, research topics, `llm_provider` + `llm_model`, concurrency, `relevance_threshold`, `output_dir`; gitignored — copy from the tracked `config.example.json`
- `pyproject.toml` - Project dependencies and metadata

## Agent Skill Packaging

- `skills/arxiv-fetch/` is a **standalone** agent skill (SKILL.md + stdlib-only `scripts/fetch_arxiv.py` + reference.md + config.example.json): the agent fetches via the script and judges relevance itself. It must keep working when copied out of the repo — never make it import from `src/` or depend on repo-root paths.
- Skill config search chain: `--subjects` flag → `--config` path → `.arxiv-fetch/config.json` in the working directory (project) → `config.json` in the skill dir (install) → `~/.config/arxiv-fetch/config.json` (user-global, XDG). The repo-root `config.json` is NOT on the chain; inside the repo, pass it via `--config` if wanted. Config UX (first-time setup, schema, managing edits) is documented in `skills/arxiv-fetch/references/config/`.
- `.claude-plugin/` holds the plugin + marketplace manifests (this repo doubles as a Claude Code plugin marketplace; install via `/plugin marketplace add yang3kc/daily_arxiv_digest`). See "Versioning & releases" below for the release procedure.
- `.gitignore` ignores `*.json` globally with explicit exceptions (`config.example.json`, the two `.claude-plugin/` manifests) — when adding a new tracked JSON file, add an exception.

## Versioning & releases

The plugin version is pinned in **`.claude-plugin/plugin.json` only** (single
source of truth; a `version` in the marketplace entry would be silently
overridden by it). Because the version is pinned, **updates are version-gated**:
pushing new commits to `main` without bumping delivers no update to existing
plugin users — Claude Code sees the same version and keeps its cache.

Cutting a release (all on `main`, after the feature branch has merged):

1. Bump `version` in `.claude-plugin/plugin.json` (semver: patch for fixes,
   minor for new skill capabilities, major for breaking config/output changes).
2. Tag the commit that contains that version and cut a matching GitHub release:
   `git tag vX.Y.Z && git push origin vX.Y.Z`, then
   `gh release create vX.Y.Z --title "vX.Y.Z" --notes "..."` — the tag and the
   manifest version must agree.
3. Version bumps cover the **skill/plugin**; changes to the digest pipeline
   (`main.py`, `src/`) don't require a bump unless they touch the skill.

## Development Notes

- The Streamlit UI was removed in the headless revamp; `digest.md` is the human-readable surface
- `digests/` is gitignored — outputs are local artifacts consumed in place by humans/agents
