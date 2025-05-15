import json
from src.llm import LLMPaperReader
from src.rss import ArxivRSS

with open("config.json") as f:
    config = json.load(f)

llm = LLMPaperReader(
    model=config["openai_model"],
    topics=config["topics"],
    timeout_seconds=config["timeout_seconds"],
)

rss_url = config["arxiv_rss_base_url"] + config["arxiv_subjects"][0]
arxiv_rss = ArxivRSS(rss_url)
paper_df = arxiv_rss.fetch_paper_list()

paper_dict_list = paper_df.to_dict(orient="records")
print(paper_dict_list)

paper_judgements_df = llm.read_papers(paper_dict_list[:10])

print(paper_judgements_df)

paper_judgements_df.to_csv("paper_judgements_df.csv", index=False)
