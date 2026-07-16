import json

from src.llm import LLMPaperReader
from src.rss import ArxivRSS

with open("config.json") as f:
    config = json.load(f)

llm = LLMPaperReader(
    provider=config["llm_provider"],
    model=config["llm_model"],
    topics=config["topics"],
    timeout_seconds=config["timeout_seconds"],
)

rss_url = config["arxiv_rss_base_url"] + config["arxiv_subjects"][0]
arxiv_rss = ArxivRSS(rss_url)
paper_df = arxiv_rss.fetch_paper_list()

paper_dict_list = paper_df.to_dict(orient="records")
print(f"Fetched {len(paper_dict_list)} papers")

sample = paper_dict_list[0]
print(llm.read_paper(sample))
print(llm.write_tldr(sample))
