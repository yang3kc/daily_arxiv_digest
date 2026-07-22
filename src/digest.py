import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.llm import LLMPaperReader
from src.logger import logger
from src.rss import ArxivRSS


def fetch_papers(config):
    """Fetch and deduplicate papers from all configured arXiv subjects."""
    logger.log_activity("fetch_papers", "started")
    paper_lists = []
    for arxiv_subject in config["arxiv_subjects"]:
        rss_url = config["arxiv_rss_base_url"] + arxiv_subject
        paper_list = ArxivRSS(rss_url).fetch_paper_list()
        print(f"Fetched {len(paper_list)} papers from {arxiv_subject}")
        paper_lists.append(paper_list)
    full_paper_list = pd.concat(paper_lists)
    if not full_paper_list.empty:
        full_paper_list = full_paper_list.drop_duplicates(subset=["id"])
    logger.log_activity(
        "fetch_papers", "completed", {"papers_count": len(full_paper_list)}
    )
    return full_paper_list


def _run_concurrently(worker, items, max_workers, label):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(worker, item) for item in items]
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                print(f"Worker failed: {e}")
            print(f"\r{label}: {len(results)}/{len(items)}", end="", flush=True)
    print()
    return results


def score_papers(llm_reader, paper_df, config):
    """Score every paper against every topic; returns papers joined with judgements."""
    logger.log_activity("llm_processing", "started")
    paper_dict_list = paper_df.to_dict(orient="records")
    judgement_dfs = _run_concurrently(
        llm_reader.read_paper,
        paper_dict_list,
        config["number_of_concurrent_tasks"],
        "Scoring papers",
    )
    judgements = pd.concat(judgement_dfs)
    if llm_reader.failure_count >= len(paper_dict_list):
        logger.log_activity(
            "llm_processing", "failed", {"failures": llm_reader.failure_count}
        )
        raise RuntimeError(
            "Every scoring call failed; aborting instead of writing an empty digest. "
            "Check the model name, API key, and provider settings."
        )
    if llm_reader.failure_count:
        print(f"Warning: {llm_reader.failure_count} papers fell back to neutral scores")
    logger.log_activity(
        "llm_processing",
        "completed",
        {"judgements_count": len(judgements), "papers_count": len(paper_dict_list)},
    )
    merged = paper_df.merge(judgements, on="id", how="left")
    merged["relevance"] = merged["relevance"].fillna(0)
    merged["reason"] = merged["reason"].fillna("")
    return merged


def select_papers(scored_df, threshold):
    """Keep judgements at or above the relevance threshold."""
    return scored_df[scored_df["relevance"] >= threshold]


def add_tldrs(llm_reader, paper_df, selected_df, config):
    """Generate one TL;DR per selected paper (papers can match several topics)."""
    selected_ids = selected_df["id"].unique()
    papers = paper_df[paper_df["id"].isin(selected_ids)].to_dict(orient="records")
    if not papers:
        return {}
    logger.log_activity("tldr_generation", "started")
    tldrs = _run_concurrently(
        llm_reader.write_tldr,
        papers,
        config["number_of_concurrent_tasks"],
        "Writing TL;DRs",
    )
    logger.log_activity("tldr_generation", "completed", {"tldr_count": len(tldrs)})
    return {item["id"]: item["tldr"] for item in tldrs}


def build_digest(date_str, paper_df, selected_df, tldrs, config):
    """Assemble the machine-readable digest record."""
    papers = []
    groups = [] if selected_df.empty else selected_df.groupby("id")
    for paper_id, group in groups:
        first = group.iloc[0]
        papers.append(
            {
                "id": paper_id,
                "title": first["title"],
                "authors": list(first["authors"]),
                "url": first["url"],
                "abstract": first["abstract"],
                "tldr": tldrs.get(paper_id, ""),
                "matched_topics": [
                    {
                        "topic": row["topic"],
                        "relevance": row["relevance"],
                        "reason": row["reason"],
                    }
                    for _, row in group.sort_values("relevance", ascending=False).iterrows()
                ],
            }
        )
    papers.sort(
        key=lambda p: max(t["relevance"] for t in p["matched_topics"]), reverse=True
    )
    return {
        "date": date_str,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "provider": config["llm_provider"],
        "model": config["llm_model"],
        "relevance_threshold": config["relevance_threshold"],
        "arxiv_subjects": config["arxiv_subjects"],
        "topics": config["topics"],
        "stats": {
            "papers_fetched": len(paper_df),
            "papers_selected": len(papers),
        },
        "papers": papers,
    }


def build_scores(date_str, scored_df, config):
    """Assemble the full scoring record: every paper with all topic judgements."""
    papers = []
    groups = [] if scored_df.empty else scored_df.groupby("id")
    for paper_id, group in groups:
        first = group.iloc[0]
        papers.append(
            {
                "id": paper_id,
                "title": first["title"],
                "authors": list(first["authors"]),
                "url": first["url"],
                "abstract": first["abstract"],
                "judgements": [
                    {
                        "topic": row["topic"],
                        "relevance": row["relevance"],
                        "reason": row["reason"],
                    }
                    for _, row in group.sort_values(
                        "relevance", ascending=False
                    ).iterrows()
                ],
            }
        )
    papers.sort(
        key=lambda p: max((j["relevance"] for j in p["judgements"]), default=0),
        reverse=True,
    )
    return {
        "date": date_str,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "provider": config["llm_provider"],
        "model": config["llm_model"],
        "arxiv_subjects": config["arxiv_subjects"],
        "topics": config["topics"],
        "papers": papers,
    }


def render_markdown(digest):
    """Render the digest record as a human-readable markdown document."""
    lines = [
        f"# arXiv digest — {digest['date']}",
        "",
        f"- Fetched {digest['stats']['papers_fetched']} papers "
        f"from {', '.join(digest['arxiv_subjects'])}",
        f"- Selected {digest['stats']['papers_selected']} papers "
        f"(relevance ≥ {digest['relevance_threshold']})",
        f"- Model: {digest['model']} ({digest['provider']})",
        "",
    ]

    if not digest["papers"]:
        lines.append("No papers passed the relevance threshold today.")
        lines.append("")
        return "\n".join(lines)

    # Group papers by topic; a paper can appear under several topics.
    papers_by_topic = {}
    for paper in digest["papers"]:
        for match in paper["matched_topics"]:
            papers_by_topic.setdefault(match["topic"], []).append((match, paper))

    for topic in digest["topics"]:
        if topic not in papers_by_topic:
            continue
        matches = sorted(
            papers_by_topic[topic], key=lambda x: x[0]["relevance"], reverse=True
        )
        lines.append(f"## {topic} ({len(matches)} papers)")
        lines.append("")
        for match, paper in matches:
            lines.append(f"### [{paper['title']}]({paper['url']})")
            lines.append("")
            lines.append(", ".join(paper["authors"]))
            lines.append("")
            if paper["tldr"]:
                lines.append(f"**TL;DR:** {paper['tldr']}")
                lines.append("")
            lines.append(f"**Relevance {match['relevance']:.2f}** — {match['reason']}")
            lines.append("")
    return "\n".join(lines)


def output_paths(output_dir, date_str):
    """Date-stamped paths for the four per-date output files.

    The output folder already carries the date, but stamping the filenames too
    keeps each file self-identifying when copied out of its folder.
    """
    output_dir = Path(output_dir)
    return {
        "json": output_dir / f"digest-{date_str}.json",
        "md": output_dir / f"digest-{date_str}.md",
        "scores": output_dir / f"scores-{date_str}.json",
        "tldrs": output_dir / f"tldrs-{date_str}.json",
    }


def write_outputs(digest, scores, output_dir, date_str):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = output_paths(output_dir, date_str)
    json_path = paths["json"]
    md_path = paths["md"]
    with open(json_path, "w") as f:
        json.dump(digest, f, indent=2, ensure_ascii=False)
    with open(paths["scores"], "w") as f:
        json.dump(scores, f, indent=2, ensure_ascii=False)
    md_path.write_text(render_markdown(digest))
    return json_path, md_path


def _load_tldr_cache(output_dir, date_str):
    cache_path = output_paths(output_dir, date_str)["tldrs"]
    if cache_path.exists():
        with open(cache_path) as f:
            return json.load(f)
    return {}


def _save_tldr_cache(output_dir, date_str, tldrs):
    cache_path = output_paths(output_dir, date_str)["tldrs"]
    with open(cache_path, "w") as f:
        json.dump(tldrs, f, indent=2, ensure_ascii=False)


def rethreshold_digest(config, date_str, output_dir, threshold):
    """Rebuild digest.json/digest.md from a saved scores.json at a new threshold.

    Skips fetching and scoring entirely; TL;DRs are reused from the existing
    digest.json and only generated for papers newly above the threshold.
    """
    output_dir = Path(output_dir)
    paths = output_paths(output_dir, date_str)
    scores_path = paths["scores"]
    if not scores_path.exists():
        raise FileNotFoundError(
            f"{scores_path} not found; run the full pipeline for this date first."
        )
    with open(scores_path) as f:
        scores = json.load(f)

    old_tldrs = _load_tldr_cache(output_dir, date_str)
    json_path = paths["json"]
    if json_path.exists():
        with open(json_path) as f:
            for paper in json.load(f)["papers"]:
                if paper.get("tldr"):
                    old_tldrs.setdefault(paper["id"], paper["tldr"])

    selected = []
    for paper in scores["papers"]:
        matched = [j for j in paper["judgements"] if j["relevance"] >= threshold]
        if matched:
            selected.append(
                {
                    "id": paper["id"],
                    "title": paper["title"],
                    "authors": paper["authors"],
                    "url": paper["url"],
                    "abstract": paper["abstract"],
                    "tldr": old_tldrs.get(paper["id"], ""),
                    "matched_topics": sorted(
                        matched, key=lambda j: j["relevance"], reverse=True
                    ),
                }
            )

    missing = [p for p in selected if not p["tldr"]]
    if missing:
        llm_reader = LLMPaperReader(
            config["llm_provider"],
            config["llm_model"],
            config["topics"],
            config["timeout_seconds"],
        )
        tldrs = _run_concurrently(
            llm_reader.write_tldr,
            missing,
            config["number_of_concurrent_tasks"],
            "Writing TL;DRs",
        )
        tldr_map = {item["id"]: item["tldr"] for item in tldrs}
        for paper in selected:
            if not paper["tldr"]:
                paper["tldr"] = tldr_map.get(paper["id"], "")
        old_tldrs.update({k: v for k, v in tldr_map.items() if v})
    _save_tldr_cache(output_dir, date_str, old_tldrs)

    digest = {
        "date": scores["date"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "provider": scores["provider"],
        "model": scores["model"],
        "relevance_threshold": threshold,
        "arxiv_subjects": scores["arxiv_subjects"],
        "topics": scores["topics"],
        "stats": {
            "papers_fetched": len(scores["papers"]),
            "papers_selected": len(selected),
        },
        "papers": selected,
    }
    with open(json_path, "w") as f:
        json.dump(digest, f, indent=2, ensure_ascii=False)
    md_path = paths["md"]
    md_path.write_text(render_markdown(digest))
    logger.log_activity(
        "rethreshold", "completed", {"threshold": threshold, "selected": len(selected)}
    )
    return digest, json_path, md_path


def run_digest(config, date_str, output_dir):
    """Run the full pipeline and write digest.json + digest.md to output_dir."""
    paper_df = fetch_papers(config)

    if paper_df.empty:
        # arXiv publishes no updates on weekends/holidays; still write a record
        # so downstream consumers can tell the run happened.
        digest = build_digest(date_str, paper_df, pd.DataFrame(), {}, config)
        scores = build_scores(date_str, pd.DataFrame(), config)
        json_path, md_path = write_outputs(digest, scores, output_dir, date_str)
        logger.log_activity("complete_run", "completed", {"papers_selected": 0})
        return digest, json_path, md_path

    llm_reader = LLMPaperReader(
        config["llm_provider"],
        config["llm_model"],
        config["topics"],
        config["timeout_seconds"],
    )
    scored_df = score_papers(llm_reader, paper_df, config)
    selected_df = select_papers(scored_df, config["relevance_threshold"])
    tldrs = add_tldrs(llm_reader, paper_df, selected_df, config)
    digest = build_digest(date_str, paper_df, selected_df, tldrs, config)
    scores = build_scores(date_str, scored_df, config)
    json_path, md_path = write_outputs(digest, scores, output_dir, date_str)
    cache = _load_tldr_cache(output_dir, date_str)
    cache.update({k: v for k, v in tldrs.items() if v})
    _save_tldr_cache(output_dir, date_str, cache)
    logger.log_activity(
        "complete_run",
        "completed",
        {"papers_selected": digest["stats"]["papers_selected"]},
    )
    return digest, json_path, md_path
