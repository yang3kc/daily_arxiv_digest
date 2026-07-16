# Introduction

Automatically generate a daily digest of interesting arXiv papers.

Having trouble catching up with the new arXiv papers everyday?
This tool fetches the latest arXiv papers, uses an LLM to rate their relevance to the topics of your interest, and writes a daily digest — a human-readable markdown file plus a machine-readable JSON file — so it can run unattended in a cron job or be driven by another agent.

# How to use

## API key

The tool supports three LLM providers, selected via `llm_provider` in `config.json`.
Export the API key for the provider you use:

| Provider | Environment variable |
|---|---|
| `openai` | `OPENAI_API_KEY` |
| `anthropic` | `ANTHROPIC_API_KEY` |
| `openrouter` | `OPENROUTER_API_KEY` |

The key can be exported in your shell, or placed in a local `.env` file in the repo root (loaded automatically via python-dotenv; see `.env.example`).
The `.env` file is gitignored, and shell-exported variables take precedence over it.

## Dependency

The tool was developed under Python 3.12.
It uses [uv](https://docs.astral.sh/uv/) to manage the dependencies.
You can install the dependencies with:

```sh
uv sync
```

## Usage

Copy `config.example.json` to `config.json` (the latter is gitignored, so your personal configuration stays local).
Then change the arXiv subjects you want to follow and the topics you are interested in.
You can also change the LLM provider and model; make sure the model supports structured output.

Generate today's digest with:

```sh
uv run python main.py
```

The digest is written to `digests/YYYY-MM-DD/`:

- `digest.md` — human-readable digest, grouped by topic, with a TL;DR for each selected paper
- `digest.json` — structured record (metadata, stats, and selected papers with scores and TL;DRs) for programmatic consumption
- `scores.json` — raw relevance scores for every fetched paper against every topic, so you can re-filter at any threshold on the fly without re-scoring

If the digest for the day already exists, the run exits cleanly without spending API calls; use `--force` to regenerate.
Other flags: `--config <path>` to use another config file, `--date YYYY-MM-DD` to label the output folder (the arXiv feed always returns the latest announcement).

The `digests/` folder is gitignored: digests are local artifacts meant to be read in place (by you or by an agent), not committed.

## Automation

The tool is designed to run unattended — e.g. a daily cron job:

```
30 9 * * 1-5 cd /path/to/daily_arxiv_digest && uv run python main.py
```

With the API key in `.env`, the cron entry needs no environment setup of its own.
Repeated invocations on the same day are no-ops, so overlapping schedules or manual re-runs are safe.
On days without arXiv announcements (weekends/holidays) it writes an empty digest so consumers can tell the run happened.

## Dev

Run a quick integration check (fetches one feed and scores one paper):

```sh
uv run python test_llm.py
```

# Disclaimer

This tool is mainly built for my personal use.
The stability of it will not be guaranteed.
Use at your own discretion.
