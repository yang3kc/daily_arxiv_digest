import json
from src.rss import ArxivRSS
from src.utils import merge_dicts
from src.llm import LLMPaperReader
import asyncio
import datetime
import os
import gzip
import pprint

if __name__ == "__main__":
    # Load config
    with open("./config.json") as f:
        config = json.load(f)
    date = datetime.datetime.now().strftime("%Y-%m-%d")

    temp_data_dir = "./data"
    if not os.path.exists(temp_data_dir):
        os.makedirs(temp_data_dir)

    # Load RSS feeds
    paper_file = os.path.join(temp_data_dir, f"{date}.json.gz")
    if os.path.exists(paper_file):
        print(f"{paper_file} exists, loading...")
        with gzip.open(paper_file, "rb") as f:
            merged_paper_list = json.loads(f.read().decode("utf-8"))
        print(f"Obtained {len(merged_paper_list)} papers in total.")
    else:
        paper_lists = []
        for arxiv_subject in config["arxiv_subjects"]:
            print(f"Fetching data from {arxiv_subject}")
            rss_url = config["arxiv_rss_base_url"] + arxiv_subject
            arss = ArxivRSS(rss_url)
            paper_list = arss.fetch_paper_list()
            print(f"Obtained {len(paper_list)} papers from {arxiv_subject}")
            paper_lists.append(paper_list)
        print("Remove duplicates...")
        merged_paper_list = merge_dicts(paper_lists)
        print(f"Obtained {len(merged_paper_list)} papers in total.")

        with gzip.open(paper_file, "wb") as f:
            bytes_to_write = json.dumps(merged_paper_list).encode("utf-8")
            f.write(bytes_to_write)

    # Read papers
    print("Reading papers ...")
    reader = LLMPaperReader(config["openai_model"], config["topics"])

    papers_already_read = set()
    judgement_file = os.path.join(temp_data_dir, f"{date}.resp.json")

    if os.path.exists(judgement_file):
        with open(judgement_file) as f:
            for line in f:
                paper = json.loads(line)
                papers_already_read.add(paper["id"])

    papers_to_read = []
    for paper in merged_paper_list.values():
        if paper["id"] not in papers_already_read:
            papers_to_read.append(paper)
    print(f"Found {len(papers_to_read)} papers to read...")

    judgement_list = asyncio.run(
        reader.read_papers(
            papers_to_read,
            number_of_concurrent_tasks=config["number_of_concurrent_tasks"],
        )
    )

    with open(os.path.join(temp_data_dir, f"{date}.resp.json"), "a") as f:
        for judgement in judgement_list:
            output = {
                "id": judgement["id"],
                "judgement": judgement["judgement"],
            }
            f.write(json.dumps(output) + "\n")
