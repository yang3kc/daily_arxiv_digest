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

Subject resolution: --subjects flag wins; otherwise arxiv_subjects from
--config (or the repo-root config.json next to this skill, if present).
"""

import argparse
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

DEFAULT_BASE_URL = "https://rss.arxiv.org/rss/"
REPO_ROOT_CONFIG = Path(__file__).resolve().parents[3] / "config.json"
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
    with urllib.request.urlopen(request, timeout=60) as response:
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


def resolve_subjects(args):
    """--subjects flag > --config file > repo-root config.json."""
    if args.subjects:
        return [s.strip() for s in args.subjects.split(",") if s.strip()], DEFAULT_BASE_URL

    config_path = Path(args.config) if args.config else REPO_ROOT_CONFIG
    if config_path.is_file():
        config = json.loads(config_path.read_text())
        subjects = config.get("arxiv_subjects", [])
        base_url = config.get("arxiv_rss_base_url", DEFAULT_BASE_URL)
        if subjects:
            return subjects, base_url

    sys.exit(
        "error: no subjects given. Pass --subjects cs.CL,cs.LG or provide a "
        f"config file with an 'arxiv_subjects' list (looked for {config_path})."
    )


def main():
    parser = argparse.ArgumentParser(description="Fetch the latest arXiv papers from RSS feeds.")
    parser.add_argument("--subjects", help="Comma-separated arXiv subject codes, e.g. cs.CL,cs.SI")
    parser.add_argument("--config", help="Path to a JSON config with an 'arxiv_subjects' list")
    parser.add_argument("--new-only", action="store_true", help="Keep only announce_type 'new' (drop cross-lists and replacements)")
    parser.add_argument("--output", help="Write JSON here instead of stdout")
    args = parser.parse_args()

    subjects, base_url = resolve_subjects(args)

    papers_by_id = {}
    by_subject = {}
    for subject in subjects:
        try:
            papers = fetch_subject(subject, base_url)
        except Exception as error:  # noqa: BLE001 — report per-feed failure, keep going
            print(f"warning: failed to fetch {subject}: {error}", file=sys.stderr)
            by_subject[subject] = 0
            continue
        by_subject[subject] = len(papers)
        for paper in papers:
            existing = papers_by_id.setdefault(paper["id"], {**paper, "subjects": []})
            existing["subjects"].append(subject)

    papers = list(papers_by_id.values())
    if args.new_only:
        papers = [p for p in papers if p["announce_type"] == "new"]

    result = {
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "subjects": subjects,
        "stats": {"papers_fetched": len(papers), "by_subject": by_subject},
        "papers": papers,
    }

    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(output + "\n")
        print(f"wrote {len(papers)} papers to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
