import streamlit as st
import json
from src.rss import ArxivRSS
from src.utils import merge_dicts
from src.llm import LLMPaperReader
import asyncio
import pandas as pd

# Load config
with open("./config.json") as f:
    config = json.load(f)


def display_papers(topic):
    threshold = st.session_state["threshold"]
    papers_to_show = st.session_state["papers_with_judgement"].query(
        f"topic == '{topic}' and relevance >= {threshold}"
    )
    st.markdown(f"## {topic} ({len(papers_to_show)} papers)")
    for _, row in papers_to_show.iterrows():
        st.markdown(f"## [{row['title']}]({row['url']})")
        st.markdown(f"{', '.join(row['authors'])}")
        with st.expander("Abstract"):
            st.markdown(row["abstract"])
        with st.expander("Judgement"):
            st.markdown(f"{row['relevance']} || {row['reason']}")


def display_papers_old(topic, paper_list):
    st.markdown(f"## {topic} ({len(paper_list)} papers)")

    for arxiv_paper in paper_list:
        st.markdown(f"## [{arxiv_paper['title']}]({arxiv_paper['url']})")
        st.markdown(f"{', '.join(arxiv_paper['authors'])}")
        with st.expander("Abstract"):
            st.markdown(arxiv_paper["abstract"])
        if "judgement" in arxiv_paper:
            with st.expander("Judgement"):
                for topic, relevance in arxiv_paper["judgement"].items():
                    if relevance["relevance"] > 0:
                        st.markdown(
                            f"{relevance['relevance']} || {topic} || {relevance['reason']}"
                        )


# @st.cache_data
def fetch_arxiv_papers(config):
    paper_lists = []
    with st.status(
        "Fetching data from arxiv", expanded=False
    ) as status:  # Changed to st.sidebar.status
        for arxiv_subject in config["arxiv_subjects"]:
            info_text = f"📡 Fetching data from {arxiv_subject}"
            st.write(info_text)
            status.update(label=info_text, state="running")
            rss_url = config["arxiv_rss_base_url"] + arxiv_subject
            arss = ArxivRSS(rss_url)
            paper_list = arss.fetch_paper_list()
            info_text = f"📄 Obtained {len(paper_list)} papers from {arxiv_subject}"
            st.write(info_text)
            status.update(label=info_text, state="running")
            paper_lists.append(paper_list)
        merged_paper_list = pd.concat(paper_lists)
        info_text = f"✅ Done obtaining {len(merged_paper_list)} papers"
        st.write(info_text)
        status.update(label=info_text, state="complete", expanded=False)
    return merged_paper_list


def classify_papers(paper_list):
    papers_by_topics = {}
    papers_by_topics["All"] = paper_list.values()
    for paper_id, paper in paper_list.items():
        for topic, relevance in paper["judgement"].items():
            if relevance["relevance"] > 0.7:
                if topic not in papers_by_topics:
                    papers_by_topics[topic] = []
                papers_by_topics[topic].append(paper)
                # print(papers_by_topics[topic])
    st.session_state["papers_by_topics"] = papers_by_topics


def llm_read_papers_old(paper_list):
    llm_reader = LLMPaperReader(
        config["openai_model"], config["topics"], config["timeout_seconds"]
    )
    papers_to_read = []
    for paper_id, paper in paper_list.items():
        if "judgement" not in paper:
            papers_to_read.append(paper)

    judgement_list = asyncio.run(
        llm_reader.read_papers(
            papers_to_read,
            number_of_concurrent_tasks=config["number_of_concurrent_tasks"],
        )
    )
    success_judgement_list = []
    for judgement in judgement_list:
        if (
            not isinstance(judgement, Exception)
            and judgement.get("judgement") is not None
        ):
            success_judgement_list.append(judgement)
    print(f"Read {len(success_judgement_list)} out of {len(judgement_list)} papers...")

    judgement_results = {}
    for judgement in success_judgement_list:
        judgement_results[judgement["id"]] = judgement["judgement"]

    paper_with_judgement = {}
    for paper_id in paper_list.keys():
        if paper_id in judgement_results:
            paper_judgement = judgement_results[paper_id]
            paper_with_judgement[paper_id] = paper_list[paper_id]
            paper_with_judgement[paper_id]["judgement"] = paper_judgement

    classify_papers(paper_with_judgement)


def llm_read_papers(paper_list):
    paper_judgements = pd.read_csv("paper_judgements_df.csv")
    paper_list_with_judgement = paper_list.merge(paper_judgements, on="id", how="left")
    paper_list_with_judgement["relevance"] = paper_list_with_judgement[
        "relevance"
    ].fillna(0)
    paper_list_with_judgement["reason"] = paper_list_with_judgement["reason"].fillna("")
    print(paper_list_with_judgement.topic.value_counts())
    st.session_state["papers_with_judgement"] = paper_list_with_judgement


# Sidebar
st.sidebar.title("arXiv digest")

if st.sidebar.button("Fetch new papers"):
    st.session_state["arxiv_papers"] = fetch_arxiv_papers(config)


if st.sidebar.button("Read papers"):
    llm_read_papers(st.session_state["arxiv_papers"])

threshold = st.sidebar.slider(
    "Relevance threshold",
    min_value=0.0,
    max_value=1.0,
    value=0.3,
    step=0.1,
    help="Papers with relevance scores above this threshold will be shown",
)
st.session_state["threshold"] = threshold


# Define selected_topic before using it
selected_topic = st.sidebar.radio(
    "Select Topic",
    []
    if "papers_with_judgement" not in st.session_state
    else list(st.session_state["papers_with_judgement"].topic.unique()),
    index=0,
)

if "papers_with_judgement" in st.session_state:
    display_papers(selected_topic)
