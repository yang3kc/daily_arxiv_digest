import json
from src.rss import ArxivRSS
from src.utils import merge_dicts
from src.llm import LLMPaperReader
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

    with open(os.path.join(temp_data_dir, f"{date}.resp.json"), "a") as f:
        count = 0
        for paper in merged_paper_list.values():
            print("--" * 10)
            print(
                f"Reading paper: {count+1} / {len(merged_paper_list)}:  {paper['title']} \n"
            )
            if paper["id"] in papers_already_read:
                print("Already read, skiping...")
                count += 1
                continue
            judgement = reader.read_paper(paper)
            pprint.pprint(judgement)
            print("\n")
            print("--" * 10)
            output = {
                "id": paper["id"],
                "judgement": judgement,
            }
            f.write(json.dumps(output) + "\n")
            count += 1
            # try:

            # except Exception as e:
            #     print(f"Error: {e}")
            # except KeyboardInterrupt:
            #     sys.exit(0)
