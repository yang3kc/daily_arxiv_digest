#!/usr/bin/env python3
"""Fetch the latest arXiv papers from RSS feeds.

Standard library only — no third-party dependencies, no API keys.
Prints a JSON document to stdout (or --output file):

{
  "fetched_at": "...",            # UTC ISO timestamp
  "subjects": ["cs.CL", ...],
  "stats": {"papers_fetched": N, "by_subject": {"cs.CL": N, ...}},
  "papers": [
    {
      "id": "2501.12345",
      "title": "...",
      "authors": ["First Last", ...],   # truncated at 10 + "..."
      "url": "https://arxiv.org/abs/2501.12345",
      "abstract": "...",
      "announce_type": "new" | "cross" | "replace" | ...,
      "subjects": ["cs.CL", ...]        # feeds this paper appeared in
    },
    ...
  ]
}

Subject resolution: --subjects flag wins; then the config file — either
--config, or the first existing file on the search chain (project
.arxiv-fetch/, then the skill directory, then ~/.config/arxiv-fetch/ —
see CONFIG_SEARCH_CHAIN). `arxiv_rss_base_url` is always read from the
config file when one is found, even when --subjects overrides the
subject list.

Failure semantics: feeds that fail (after one retry) are listed in
stats.failed_subjects; the process exits nonzero if every feed failed,
so an empty papers[] with exit 0 and no failed_subjects really means
"no announcements" (weekend/holiday).
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

DEFAULT_BASE_URL = "https://rss.arxiv.org/rss/"
SKILL_DIR = Path(__file__).resolve().parents[1]
XDG_CONFIG_HOME = Path(os.environ.get("XDG_CONFIG_HOME", "~/.config")).expanduser()
CONFIG_SEARCH_CHAIN = [
    Path.cwd() / ".arxiv-fetch" / "config.json",  # project-local (per-project interests)
    SKILL_DIR / "config.json",  # install-local (copy/clone installs)
    XDG_CONFIG_HOME / "arxiv-fetch" / "config.json",  # user-global; survives plugin updates
]
NAMESPACES = {"dc": "http://purl.org/dc/elements/1.1/"}
MAX_AUTHORS = 10


class _TextExtractor(HTMLParser):
    """Strip HTML tags, keeping text content (replaces BeautifulSoup)."""

    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    @classmethod
    def strip(cls, html_string):
        extractor = cls()
        extractor.feed(html_string)
        return "".join(extractor.parts)


def _clean_abstract(description):
    """Extract the abstract from an arXiv RSS description.

    Descriptions look like: "arXiv:2501.12345v1 Announce Type: new
    Abstract: <the abstract text>". Fall back to the whole description
    if the marker is absent.
    """
    text = _TextExtractor.strip(description)
    match = re.search(r"Abstract:\s*(.*)", text, flags=re.DOTALL)
    abstract = match.group(1) if match else text
    return re.sub(r"\s+", " ", abstract).strip()


def _extract_arxiv_id(item):
    """Normalize an arXiv id like '2501.12345' from guid or link."""
    for field in ("guid", "link"):
        element = item.find(field)
        if element is not None and element.text:
            match = re.search(r"(\d{4}\.\d{4,5})(v\d+)?", element.text)
            if match:
                return match.group(1)
    return None


def _parse_authors(item):
    creator = item.find("dc:creator", NAMESPACES)
    if creator is None or not creator.text:
        return []
    authors = [name.strip() for name in creator.text.split(",") if name.strip()]
    if len(authors) > MAX_AUTHORS:
        authors = authors[:MAX_AUTHORS] + ["..."]
    return authors


def _parse_announce_type(item):
    # <arxiv:announce_type> lives in a namespace that varies across
    # feed versions; match on the local tag name instead.
    for element in item.iter():
        if element.tag.endswith("announce_type"):
            return (element.text or "").strip()
    return ""


def fetch_subject(subject, base_url):
    """Fetch one subject feed, return a list of paper dicts."""
    url = base_url.rstrip("/") + "/" + subject
    request = urllib.request.Request(url, headers={"User-Agent": "arxiv-fetch-skill"})
    with urllib.request.urlopen(request, timeout=30) as response:
        root = ET.fromstring(response.read())

    papers = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        description = item.findtext("description") or ""
        paper_id = _extract_arxiv_id(item)
        papers.append(
            {
                "id": paper_id or title,
                "title": title,
                "authors": _parse_authors(item),
                "url": f"https://arxiv.org/abs/{paper_id}" if paper_id else (item.findtext("link") or "").strip(),
                "abstract": _clean_abstract(description),
                "announce_type": _parse_announce_type(item),
            }
        )
    return papers


def load_config(args):
    """Return (config dict, path) from --config or the search chain; ({}, None) if absent."""
    if args.config:
        config_path = Path(args.config)
        if not config_path.is_file():
            sys.exit(f"error: config file not found: {config_path}")
        candidates = [config_path]
    else:
        candidates = CONFIG_SEARCH_CHAIN

    for config_path in candidates:
        if config_path.is_file():
            try:
                config = json.loads(config_path.read_text())
            except json.JSONDecodeError as error:
                sys.exit(f"error: invalid JSON in {config_path}: {error}")
            if not isinstance(config, dict):
                sys.exit(f"error: {config_path} must contain a JSON object.")
            return config, config_path
    return {}, None


def resolve_inputs(args):
    """Return (subjects, base_url).

    Subjects: --subjects flag > config 'arxiv_subjects'. The base URL is
    read from the config file whenever one exists (even under --subjects),
    falling back to DEFAULT_BASE_URL.
    """
    config, config_path = load_config(args)

    base_url = config.get("arxiv_rss_base_url", DEFAULT_BASE_URL)
    if not isinstance(base_url, str) or not base_url.strip():
        sys.exit(f"error: 'arxiv_rss_base_url' in {config_path} must be a non-empty string.")

    if args.subjects:
        subjects = [s.strip() for s in args.subjects.split(",") if s.strip()]
        if subjects:
            return subjects, base_url

    subjects = config.get("arxiv_subjects", [])
    if not isinstance(subjects, list) or not all(
        isinstance(s, str) and s.strip() for s in subjects
    ):
        sys.exit(
            f"error: 'arxiv_subjects' in {config_path} must be a list of "
            "non-empty strings (e.g. [\"cs.CL\", \"cs.LG\"])."
        )
    if subjects:
        return [s.strip() for s in subjects], base_url

    searched = ", ".join(str(path) for path in ([config_path] if config_path else CONFIG_SEARCH_CHAIN))
    sys.exit(
        "error: no subjects given. Pass --subjects cs.CL,cs.LG or provide a "
        f"config file with an 'arxiv_subjects' list (searched: {searched})."
    )


def fetch_subject_with_retry(subject, base_url):
    """Fetch a feed, retrying once on failure. Returns (papers, error)."""
    for attempt in (1, 2):
        try:
            return fetch_subject(subject, base_url), None
        except Exception as error:  # noqa: BLE001 — per-feed isolation; reported upstream
            if attempt == 1:
                print(f"warning: {subject} failed ({error}), retrying...", file=sys.stderr)
            else:
                return [], error
    return [], None  # unreachable


def main():
    parser = argparse.ArgumentParser(description="Fetch the latest arXiv papers from RSS feeds.")
    parser.add_argument("--subjects", help="Comma-separated arXiv subject codes, e.g. cs.CL,cs.SI")
    parser.add_argument("--config", help="Path to a JSON config with an 'arxiv_subjects' list")
    parser.add_argument("--new-only", action="store_true", help="Keep only announce_type 'new' (drop cross-lists and replacements)")
    parser.add_argument("--output", help="Write JSON here instead of stdout")
    args = parser.parse_args()

    subjects, base_url = resolve_inputs(args)

    with ThreadPoolExecutor(max_workers=min(8, len(subjects))) as pool:
        results = list(pool.map(lambda s: fetch_subject_with_retry(s, base_url), subjects))

    papers_by_id = {}
    by_subject = {}
    failed_subjects = []
    for subject, (papers, error) in zip(subjects, results):
        if error is not None:
            print(f"warning: failed to fetch {subject}: {error}", file=sys.stderr)
            failed_subjects.append(subject)
            by_subject[subject] = 0
            continue
        by_subject[subject] = len(papers)
        for paper in papers:
            existing = papers_by_id.get(paper["id"])
            if existing is None:
                papers_by_id[paper["id"]] = {**paper, "subjects": [subject]}
            else:
                existing["subjects"].append(subject)
                # A paper can be "new" in its primary feed but "cross" in
                # others — keep "new" regardless of which feed came first.
                if paper["announce_type"] == "new":
                    existing["announce_type"] = "new"

    if failed_subjects and len(failed_subjects) == len(subjects):
        sys.exit(f"error: all feeds failed ({', '.join(failed_subjects)}); no output written.")

    papers = list(papers_by_id.values())
    if args.new_only:
        papers = [p for p in papers if p["announce_type"] == "new"]

    result = {
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "subjects": subjects,
        "stats": {
            "papers_fetched": len(papers),
            "by_subject": by_subject,
            "failed_subjects": failed_subjects,
        },
        "papers": papers,
    }

    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        output_path = Path(args.output)
        if output_path.parent != Path("."):
            output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output + "\n")
        print(f"wrote {len(papers)} papers to {args.output}", file=sys.stderr)
    else:
        print(output)
    if failed_subjects:
        print(
            f"warning: {len(failed_subjects)} of {len(subjects)} feeds failed: "
            f"{', '.join(failed_subjects)} — results are partial.",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
