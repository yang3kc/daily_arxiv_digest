

# Introduction

Automatically generate a daily digest of interesting arXiv papers.

Having trouble catching up with the new arXiv papers everyday?
This tool fetches the latest arXiv papers, uses an LLM to rate their relevance to the topics of your interest, and writes a daily digest — a human-readable markdown file plus a machine-readable JSON file — so it can run unattended in a cron job or be driven by another agent.

It comes in two forms:

- **Daily digest pipeline** (this section and below) — the full pipeline with its own LLM calls, designed to run unattended (e.g. daily cron). Needs an API key.
- **[Agent skill](#agent-skill)** — a standalone skill for AI agents (e.g. Claude Code): the agent fetches the papers and judges relevance itself. No API key, no dependencies, no repo clone needed — just any Python 3.

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

The digest is written to `digests/YYYY-MM-DD/`, with the date stamped into every filename so the files stay self-identifying when copied out of their folder:

- `digest-YYYY-MM-DD.md` — human-readable digest, grouped by topic, with a TL;DR for each selected paper
- `digest-YYYY-MM-DD.json` — structured record (metadata, stats, and selected papers with scores and TL;DRs) for programmatic consumption
- `scores-YYYY-MM-DD.json` — raw relevance scores for every fetched paper against every topic, so you can re-filter at any threshold on the fly without re-scoring

If the digest for the day already exists, the run exits cleanly without spending API calls; use `--force` to regenerate.
Other flags: `--config <path>` to use another config file, `--date YYYY-MM-DD` to label the output folder (the arXiv feed always returns the latest announcement).

To re-render the digest at a different threshold without re-fetching or re-scoring:

```sh
uv run python main.py --rethreshold 0.9
```

This rebuilds `digest-YYYY-MM-DD.md`/`digest-YYYY-MM-DD.json` from the saved `scores-YYYY-MM-DD.json`; TL;DRs are cached in `tldrs-YYYY-MM-DD.json`, so changing the threshold back and forth costs no API calls once a paper's TL;DR has been generated.

The `digests/` folder is gitignored: digests are local artifacts meant to be read in place (by you or by an agent), not committed.

## Automation

The tool is designed to run unattended — e.g. a daily cron job:

```
30 9 * * 1-5 cd /path/to/daily_arxiv_digest && uv run python main.py
```

With the API key in `.env`, the cron entry needs no environment setup of its own.
Repeated invocations on the same day are no-ops, so overlapping schedules or manual re-runs are safe.
On days without arXiv announcements (weekends/holidays) it writes an empty digest so consumers can tell the run happened.

# Agent skill

`skills/arxiv-fetch/` packages the fetch capability as a standalone skill for AI agents (e.g. Claude Code).

## How it works

The daily pipeline pays an LLM API to score papers because it runs unattended. When an agent is invoked, there is already an LLM in the loop — so the skill only automates the one thing the agent cannot do natively (fetching the RSS feeds) and lets the agent do the judging itself. That is why the skill needs no API key, no dependency install, and no repo clone: just any Python 3.

Ask your agent something like *"fetch today's arXiv papers"* or *"any new papers on LLM persuasion?"* and it will:

1. **Resolve subjects and topics.** Anything explicit in your request wins; otherwise defaults come from your config (see below). If you name a topic but no subject, the agent picks likely feeds from the bundled [category taxonomy](skills/arxiv-fetch/references/arxiv-categories.md). With neither config nor a specific request, a short first-time setup asks for your interests and saves them.
2. **Fetch.** The agent runs `scripts/fetch_arxiv.py` (stdlib-only), which pulls the feeds concurrently with retries, dedupes papers announced in several feeds, and reports failed feeds explicitly — so an empty result genuinely means "no announcements today" (weekend/holiday), never a swallowed network error.
3. **Judge.** The agent reads titles and abstracts and selects against your topics — instructed to be selective: papers a researcher on that topic would actually open.
4. **Digest.** You get a digest grouped by topic — linked title, authors, and a TL;DR focused on why the paper matches — plus fetched-vs-selected counts. Saved to a file only if you ask.

## Skill configuration

Defaults live in a small `config.json` (`arxiv_subjects` + `topics`), searched in order:

1. `.arxiv-fetch/config.json` in the working directory — per-project interests
2. `config.json` inside the skill folder — install-local
3. `~/.config/arxiv-fetch/config.json` — user-global; survives plugin updates

Explicit subjects/topics in a request always override the config without modifying it. You never need to hand-edit the file: ask the agent to *show*, *change*, *move*, or *reset* your arxiv config, or to set up project-specific topics ("use different topics for this project"). Details: [schema](skills/arxiv-fetch/references/config/schema.md), [first-time setup](skills/arxiv-fetch/references/config/first-time-setup.md).

## Installation

The skill lives in `skills/arxiv-fetch/` and follows the portable `SKILL.md`
convention, so any agent that reads markdown instruction files can use it.
Compatible with Claude Code, Cursor, Windsurf, GitHub Copilot, and others.
Pick whichever install approach fits your agent.

### Claude Code plugin (recommended)

This repo doubles as a Claude Code plugin marketplace. Add it, then install
the `arxiv-fetch` plugin — this registers the skill and keeps it updatable:

```
/plugin marketplace add yang3kc/daily_arxiv_digest
/plugin install arxiv-fetch@daily-arxiv-digest
```

The same works from the terminal: `claude plugin marketplace add
yang3kc/daily_arxiv_digest`, then `claude plugin install
arxiv-fetch@daily-arxiv-digest`.

With this route, keep your config in the user-global location
(`~/.config/arxiv-fetch/config.json`) — it survives plugin updates, unlike a
config inside the skill folder (see the precedence above).

#### Updates

Skill updates ship as versioned
[releases](https://github.com/yang3kc/daily_arxiv_digest/releases): the
plugin version is pinned, so you get a new version exactly when a release is
cut — commits between releases don't change your installed copy. To update:

1. Run `/plugin` in Claude Code
2. Switch to the **Marketplaces** tab
3. Select **daily-arxiv-digest** and choose **Update marketplace**

You can also **Enable auto-update** there to pick up new releases
automatically.

### Copy without cloning

Extract just the skill folder from the repo tarball:

```sh
mkdir -p ~/.claude/skills
curl -L https://github.com/yang3kc/daily_arxiv_digest/archive/refs/heads/main.tar.gz \
  | tar -xz --strip-components=2 -C ~/.claude/skills daily_arxiv_digest-main/skills/arxiv-fetch
```

### Clone into your agent's skills directory

Clone the repo, then point your agent at the skill folder:

```bash
# Claude Code — clone, then symlink the skill into ~/.claude/skills/
git clone git@github.com:yang3kc/daily_arxiv_digest.git ~/src/daily_arxiv_digest
ln -s ~/src/daily_arxiv_digest/skills/arxiv-fetch ~/.claude/skills/arxiv-fetch

# Cursor — link into your project (or global) rules/skills directory
ln -s ~/src/daily_arxiv_digest/skills/arxiv-fetch .cursor/skills/arxiv-fetch

# Any agent — clone anywhere, then point it at skills/arxiv-fetch/SKILL.md
git clone git@github.com:yang3kc/daily_arxiv_digest.git /path/to/daily_arxiv_digest
```

### `skills` CLI

For agents that support the [`vercel-labs/skills`](https://github.com/vercel-labs/skills) CLI:

```bash
npx skills install https://github.com/yang3kc/daily_arxiv_digest
```

Once the skill is available to your agent, it activates automatically when your
request matches its description.

## Relationship to the pipeline

The two modes are complementary and share nothing at runtime: the cron pipeline is the unattended daily producer with its own config and LLM budget; the skill is the on-demand path for whatever you ask, whenever you ask. You can run both.

# Dev

Run a quick integration check (fetches one feed and scores one paper; it uses `config.json` and an API key):

```sh
uv run python test_llm.py
```

# Disclaimer

This tool is mainly built for my personal use.
The stability of it will not be guaranteed.
Use at your own discretion.
