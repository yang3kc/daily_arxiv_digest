# Config Schema

## File and search chain

`config.json` — plain JSON, searched in order (first match wins; the fetch
script walks the same chain for subjects):

| Priority | Path | Scope | Survives skill updates? |
|---|---|---|---|
| 1 | `.arxiv-fetch/config.json` (working directory) | Project | Yes (user-owned) |
| 2 | `config.json` in the skill directory | Install | **No** for plugin installs; yes for copied/cloned installs |
| 3 | `~/.config/arxiv-fetch/config.json` (`$XDG_CONFIG_HOME` respected) | User-global | Yes |

Per-invocation `--subjects` / `--config` flags and explicit subjects/topics
in the user's request override any file.

## Fields

| Field | Type | Required | Used by | Description |
|---|---|---|---|---|
| `arxiv_subjects` | string[] | Yes | fetch script | arXiv feed codes to fetch (see [../arxiv-categories.md](../arxiv-categories.md)) |
| `topics` | string[] | Yes* | agent | Natural-language research interests the agent selects papers for |
| `arxiv_rss_base_url` | string | No | fetch script | Feed base URL; default `https://rss.arxiv.org/rss/` |

*Required for default digests ("fetch today's papers" with no topic named);
a request that names its own topic works without it.

Unknown fields are ignored — a richer config (e.g. the daily_arxiv_digest
pipeline's `config.json`, which shares these field names) works as-is via
`--config`.

## Examples

Minimal:

```json
{
    "arxiv_subjects": ["cs.CL", "cs.LG"],
    "topics": ["LLM evaluation and benchmarking"]
}
```

Full:

```json
{
    "arxiv_subjects": ["cs.SI", "cs.CY", "physics.soc-ph"],
    "topics": [
        "Misinformation and fact-checking on social media",
        "LLM-based agents simulating social behavior"
    ],
    "arxiv_rss_base_url": "https://rss.arxiv.org/rss/"
}
```
