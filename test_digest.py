"""Offline unit checks for markdown rendering (no API keys / network needed).

Run with: uv run python test_digest.py
Covers the cross-topic note behavior shared by run_digest and --rethreshold,
plus the short-label helpers.
"""

import json
import tempfile
from pathlib import Path

import pandas as pd

from src.digest import (
    add_tldrs,
    _load_tldr_cache,
    _short_topic,
    _topic_labels,
    output_paths,
    render_markdown,
)
from src.llm import LLMPaperReader

TOPIC_A = "Security and safety of AI and language models"
TOPIC_B = "Factuality of AI systems, misinformation, and fact-checking"
TOPIC_C = "AI and health information seeking, including AI chatbots"


def _paper(title, topics):
    return {
        "id": title,
        "title": title,
        "authors": ["Ada Lovelace"],
        "url": f"https://arxiv.org/abs/{title}",
        "abstract": "",
        "tldr": "A short summary.",
        "matched_topics": [
            {"topic": t, "relevance": r, "reason": "because"} for t, r in topics
        ],
    }


def _digest(papers, topics):
    return {
        "date": "2026-07-22",
        "provider": "openai",
        "model": "gpt-5-mini",
        "relevance_threshold": 0.8,
        "arxiv_subjects": ["cs.CY"],
        "topics": topics,
        "stats": {"papers_fetched": 100, "papers_selected": len(papers)},
        "papers": papers,
    }


def test_single_topic_paper_has_no_note():
    md = render_markdown(_digest([_paper("solo", [(TOPIC_A, 0.9)])], [TOPIC_A]))
    assert "Also matches" not in md


def test_two_topics_uses_singular_noun():
    paper = _paper("dual", [(TOPIC_A, 0.95), (TOPIC_B, 0.9)])
    md = render_markdown(_digest([paper], [TOPIC_A, TOPIC_B]))
    # Appears under both sections; each occurrence names the *other* topic only.
    assert md.count("Also matches 1 other topic:") == 2
    assert "Also matches 1 other topics" not in md  # correct singular
    # Under the A section the note points to B, and vice versa.
    a_idx, b_idx = md.index(f"## {TOPIC_A}"), md.index(f"## {TOPIC_B}")
    a_note = md[a_idx:b_idx]
    assert _short_topic(TOPIC_B) in a_note and _short_topic(TOPIC_A) not in a_note


def test_three_topics_uses_plural_noun():
    paper = _paper("triple", [(TOPIC_A, 0.95), (TOPIC_B, 0.9), (TOPIC_C, 0.85)])
    md = render_markdown(_digest([paper], [TOPIC_A, TOPIC_B, TOPIC_C]))
    assert md.count("Also matches 2 other topics:") == 3


def test_short_topic_respects_limit_and_word_boundary():
    label = _short_topic(TOPIC_A, limit=30)
    assert len(label) <= 30
    assert label.endswith("…")
    assert " " not in label[-2:-1]  # no trailing partial word before the ellipsis
    # No-space prefix falls back to a hard cut but still respects the limit.
    hard = _short_topic("Supercalifragilisticexpialidocious", limit=10)
    assert len(hard) <= 10 and hard.endswith("…")
    # Short topics pass through untouched.
    assert _short_topic("Climate", limit=30) == "Climate"


def test_ambiguous_prefixes_fall_back_to_full_labels():
    t1 = "Applications of machine learning in healthcare systems"
    t2 = "Applications of machine learning in education systems"
    labels = _topic_labels([t1, t2], limit=30)
    # Both would shorten identically, so both keep their full text to stay distinct.
    assert labels[t1] == t1 and labels[t2] == t2
    assert labels[t1] != labels[t2]


def test_empty_digest_renders_placeholder():
    md = render_markdown(_digest([], [TOPIC_A]))
    assert "No papers passed the relevance threshold today." in md
    assert "Also matches" not in md


class _ExplodingReader:
    """A TL;DR reader that fails the test if it is ever called."""

    def write_tldr(self, paper, max_retries=3):
        raise AssertionError("write_tldr should not run for a fully cached paper")


def test_add_tldrs_reuses_cache_without_querying():
    paper_df = pd.DataFrame(
        [{"id": "p1", "title": "t", "abstract": "a", "url": "u", "authors": ["x"]}]
    )
    selected_df = pd.DataFrame([{"id": "p1", "topic": TOPIC_A, "relevance": 0.9}])
    config = {"number_of_concurrent_tasks": 2}
    # Every selected paper is cached, so no LLM call should happen.
    result = add_tldrs(
        _ExplodingReader(), paper_df, selected_df, config, cached={"p1": "cached tldr"}
    )
    assert result == {"p1": "cached tldr"}


class _StubReader:
    """A TL;DR reader that returns a deterministic generated summary."""

    def write_tldr(self, paper, max_retries=3):
        return {"id": paper["id"], "tldr": f"generated:{paper['id']}"}


def test_add_tldrs_only_generates_missing_papers():
    paper_df = pd.DataFrame(
        [
            {"id": "p1", "title": "t1", "abstract": "a1", "url": "u1", "authors": ["x"]},
            {"id": "p2", "title": "t2", "abstract": "a2", "url": "u2", "authors": ["y"]},
        ]
    )
    selected_df = pd.DataFrame(
        [
            {"id": "p1", "topic": TOPIC_A, "relevance": 0.9},
            {"id": "p2", "topic": TOPIC_A, "relevance": 0.85},
        ]
    )
    config = {"number_of_concurrent_tasks": 2}
    # p1 is cached (reused); p2's cache entry is empty, so it must be regenerated.
    result = add_tldrs(
        _StubReader(), paper_df, selected_df, config, cached={"p1": "cached", "p2": ""}
    )
    assert result == {"p1": "cached", "p2": "generated:p2"}


def test_format_topics_is_a_clean_bulleted_block():
    block = LLMPaperReader._format_topics([TOPIC_A, TOPIC_B])
    assert block == f"- {TOPIC_A}\n- {TOPIC_B}"
    assert "[" not in block and "'" not in block  # not a Python list repr
    # A bare string is treated as a single topic.
    assert LLMPaperReader._format_topics("solo") == "- solo"


def test_scoring_prompt_puts_static_prefix_before_paper():
    # Guards the caching optimization: the static rubric + topics must precede
    # the per-paper title/abstract, or the shared prefix stops being cacheable.
    prompt = LLMPaperReader.user_message.format(
        topics=LLMPaperReader._format_topics([TOPIC_A, TOPIC_B]),
        title="THE_TITLE",
        abstract="THE_ABSTRACT",
    )
    topics_at = prompt.index(TOPIC_A)
    rubric_at = prompt.index("Be strict and discriminating")
    title_at = prompt.index("THE_TITLE")
    abstract_at = prompt.index("THE_ABSTRACT")
    assert topics_at < title_at and rubric_at < title_at
    assert title_at < abstract_at


def test_load_tldr_cache_tolerates_malformed_files():
    with tempfile.TemporaryDirectory() as d:
        out = Path(d)
        cache_path = output_paths(out, "2026-07-22")["tldrs"]
        # Missing file -> empty.
        assert _load_tldr_cache(out, "2026-07-22") == {}
        # Invalid JSON -> empty, no crash.
        cache_path.write_text("{not json")
        assert _load_tldr_cache(out, "2026-07-22") == {}
        # Wrong top-level type -> empty.
        cache_path.write_text(json.dumps(["a", "b"]))
        assert _load_tldr_cache(out, "2026-07-22") == {}
        # Non-string values are dropped; valid string entries survive.
        cache_path.write_text(json.dumps({"p1": "ok", "p2": 5, "p3": None}))
        assert _load_tldr_cache(out, "2026-07-22") == {"p1": "ok"}


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        test()
        print(f"ok  {test.__name__}")
    print(f"\n{len(tests)} passed")
