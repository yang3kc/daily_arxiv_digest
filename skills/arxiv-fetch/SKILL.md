---
name: arxiv-fetch
description: Fetch the latest arXiv papers and generate an on-demand digest. Use when the user asks to fetch/check today's (or the latest) arXiv papers, find new papers on a topic, or generate an ad-hoc arXiv digest. The agent judges relevance itself — no API keys needed.
---

# arXiv Fetch & Digest

Fetch the latest papers from arXiv RSS feeds, judge their relevance to the
user's topics **yourself** (you are the LLM — no external API calls), and
present a digest. Fully standalone: the fetch script is Python-stdlib-only,
needs no API keys, and no other files beyond this skill directory.

## Step 1 — Resolve subjects and topics

Two inputs, resolved independently, same precedence:

1. **From the request.** Explicit subjects ("check cs.SI") or topics ("papers
   about LLM persuasion") in the user's message always win. Free-form topic
   phrasing is fine — you are the judge; no schema. If the user names a topic
   but no subject, infer likely subjects from
   [references/arxiv-categories.md](references/arxiv-categories.md).
2. **From config.** A JSON file with `arxiv_subjects` (feed codes) and
   `topics` (natural-language interests). Searched in order — project
   (`.arxiv-fetch/config.json` in the working directory), install
   (`config.json` in this skill directory), then user-global
   (`~/.config/arxiv-fetch/config.json`). Full details:
   [references/config/schema.md](references/config/schema.md). The fetch
   script walks the same chain automatically for subjects; read the same
   file for topics.
3. **Neither available?** Run the first-time setup flow:
   [references/config/first-time-setup.md](references/config/first-time-setup.md).
   It is blocking when the request doesn't say what to fetch; otherwise
   proceed and offer to save afterwards.

## Step 2 — Fetch

```sh
python3 scripts/fetch_arxiv.py --subjects cs.SI,cs.CY --output <scratchpad>/arxiv.json
```

(Any Python 3; run from this skill directory, or call the script by its
absolute path.) Flags:

- `--subjects a,b,c` — override config subjects
- `--config <path>` — explicit config file, skipping the search chain
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

Only if the user asks to save the digest, write it where they specify
(default suggestion: `arxiv-digest-YYYY-MM-DD-<slug>.md` in the current
working directory). For machine consumers, mirror the fetch JSON shape:
keep each selected paper's fields and add `tldr` plus
`matched_topics[] {topic, reason}`, with papers grouped or tagged by topic.

## Changing your config

Handle these directly when asked — the user should never need to hand-edit:

- **"Show my arxiv config"** — print the active config file's path and
  contents (walk the chain in [references/config/schema.md](references/config/schema.md);
  say which file won and which others exist).
- **"Change my subjects/topics"** — edit the active config file in place;
  confirm the new values. Map informal names to codes via
  [references/arxiv-categories.md](references/arxiv-categories.md).
- **"Use different topics for this project"** — create
  `.arxiv-fetch/config.json` in the project (it outranks user-global);
  suggest gitignoring it if personal.
- **"Move my config"** / scope change — copy the file to the new location,
  delete the old one, confirm both paths.
- **"Reset / start over"** — delete the config(s) they name, then re-run
  [references/config/first-time-setup.md](references/config/first-time-setup.md).

One-off requests ("just check cs.CY today") are overrides — never write
them into the config unless asked to make them the default.
