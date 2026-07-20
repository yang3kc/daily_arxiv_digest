---
name: arxiv-fetch
description: Fetch the latest arXiv papers and generate an on-demand digest. Use when the user asks to fetch/check today's (or the latest) arXiv papers, find new papers on a topic, or generate an ad-hoc arXiv digest. The agent judges relevance itself — no API keys needed.
---

# arXiv Fetch & Digest

Fetch the latest papers from arXiv RSS feeds, judge their relevance to the
user's topics **yourself** (you are the LLM — no external API calls), and
present a digest.

## Step 1 — Resolve subjects and topics

Two inputs, resolved independently, same precedence:

1. **From the request.** Explicit subjects ("check cs.SI") or topics ("papers
   about LLM persuasion") in the user's message always win. Free-form topic
   phrasing is fine — you are the judge; no schema. If the user names a topic
   but no subject, infer likely subjects from [reference.md](reference.md).
2. **From config.** `config.json` at the repo root (fields: `arxiv_subjects`,
   `topics`) — the same file the cron pipeline uses. The fetch script reads
   `arxiv_subjects` from it automatically when `--subjects` is not passed.
3. **Neither available?** Ask the user, and offer to create `config.json`
   from `config.example.json` so they don't have to specify next time.

## Step 2 — Fetch

```sh
python3 scripts/fetch_arxiv.py --subjects cs.SI,cs.CY --output <scratchpad>/arxiv.json
```

Stdlib-only (any Python 3), no keys. Flags:

- `--subjects a,b,c` — override config subjects
- `--config <path>` — alternate config file
- `--new-only` — drop cross-lists (`cross`) and revisions (`replace`); use
  this by default unless the user wants everything
- `--output <path>` — write to a file instead of stdout (prefer this; write
  to the scratchpad, then read/process in slices)

Output: `{fetched_at, subjects, stats, papers[]}`; each paper has `id`,
`title`, `authors[]`, `url`, `abstract`, `announce_type`, `subjects[]`
(papers appearing in several feeds are deduplicated, all feeds listed).
Author names may contain raw TeX accents (`Ra\'ul`) — render them properly
in any digest you write.

Weekends/holidays have no announcements — an empty `papers[]` is a normal
result, not an error; tell the user there were no new announcements.

## Step 3 — Judge relevance

Read the fetched papers (title + abstract) and judge each against the topics.
Be selective: the digest's value is filtering, so "somewhat related" is not
enough — select papers a researcher on that topic would actually open.

For large batches (a busy day on cs.CL can exceed 200 papers), process the
JSON in slices so nothing is skipped, or fan out subagents per slice/topic
and merge their selections.

## Step 4 — Digest

Present in chat, grouped by topic: title (linked to `url`), authors, and a
one-to-two-sentence TL;DR in your own words focused on what's relevant to
the topic. Note total fetched vs. selected so the user knows the coverage.

Only if the user asks to save it, write to `digests/<date>-adhoc-<slug>/`
in this repo (gitignored), mirroring the cron pipeline's `digest.md` +
`digest.json` contract (see AGENTS.md "Output Contract") so downstream
consumers can treat both alike.
