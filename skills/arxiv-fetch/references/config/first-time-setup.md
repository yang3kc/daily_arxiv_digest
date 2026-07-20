# First-Time Setup

## When to run

Run this flow when **no config file exists** on the search chain (see
[schema.md](schema.md)) **and** the user's request doesn't fully specify what
to fetch:

- Request has subjects **and** topics → skip setup, proceed; after
  delivering the digest, offer once to save them as defaults.
- Request has topics but no subjects → infer subjects from
  [../arxiv-categories.md](../arxiv-categories.md), proceed, then offer to save.
- Request has neither (e.g. just "fetch today's arXiv papers") → **setup is
  blocking**: complete it before fetching anything.

Never re-run setup when a config exists — see "Changing your config" in
SKILL.md for edits.

## Setup flow

Ask (via AskUserQuestion or your platform's equivalent; plain-text questions
as a last resort — but never silently skip):

### Question 1: Subjects

```yaml
header: "Subjects"
question: "Which arXiv subject feeds should be fetched by default?"
multiSelect: true
options:
  - label: "cs.CL + cs.LG"
    description: "NLP / LLMs and machine learning"
  - label: "cs.SI + cs.CY"
    description: "Social networks and computers & society"
  - label: "cs.AI + cs.MA"
    description: "AI and multiagent systems"
```

Users with other interests answer free-form ("Other"); map their answer to
subject codes using [../arxiv-categories.md](../arxiv-categories.md) and
confirm the codes you picked.

### Question 2: Topics

Ask in free text (no fixed options — topics are personal):

> "Describe the research topics you want the digest to select for — a few
> natural-language phrases, as specific as you like (e.g. 'LLM evaluation
> and benchmarking', 'misinformation on social media')."

### Question 3: Save location

```yaml
header: "Save where"
question: "Where should these defaults be saved?"
options:
  - label: "User-global (Recommended)"
    description: "~/.config/arxiv-fetch/config.json — applies everywhere, survives skill updates"
  - label: "Project"
    description: ".arxiv-fetch/config.json in this project — this project only"
  - label: "Install-local"
    description: "config.json inside the skill folder — lost on plugin updates; only for self-managed installs"
```

## After the answers

1. Create the directory if needed and write the config (shape:
   [../../config.example.json](../../config.example.json); fields:
   [schema.md](schema.md)).
2. If saving to a **project** location, remind the user to add
   `.arxiv-fetch/` to `.gitignore` if the project is shared and their
   interests are personal.
3. Confirm: "Defaults saved to `<path>` — say 'change my arxiv config' to
   edit them later."
4. Continue with the fetch.
