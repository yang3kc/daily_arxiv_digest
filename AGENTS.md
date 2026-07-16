# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository. (CLAUDE.md includes it via `@AGENTS.md`.)

## Project Overview

Daily arXiv Digest is a headless CLI tool that fetches papers from arXiv RSS feeds, uses an LLM to rate their relevance against user-defined topics, and writes a daily digest to `digests/YYYY-MM-DD/` as both markdown (for humans) and JSON (for agents). It is designed to run unattended in a cron job or be invoked by another agent.

## Commands

### Development and Running
- `make run` or `make all` - Generate today's digest
- `uv run python main.py` - Direct command (flags: `--config`, `--date`, `--force`)
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

## Development Notes

- The Streamlit UI was removed in the headless revamp; `digest.md` is the human-readable surface
- `digests/` is gitignored — outputs are local artifacts consumed in place by humans/agents
