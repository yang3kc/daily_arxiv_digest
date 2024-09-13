import streamlit as st
import pandas as pd
import json
import time
from src.rss import ArxivRSS
from src.utils import merge_dicts

# Load config
with open("./config.json") as f:
    config = json.load(f)


def display_papers(topic, paper_list):
    st.markdown(f"## {topic} ({len(paper_list)} papers)")

    for arxiv_paper in paper_list:
        st.markdown(f"## [{arxiv_paper['title']}]({arxiv_paper['url']})")
        st.markdown(f"{', '.join(arxiv_paper['authors'])}")
        with st.expander("Abstract"):
            st.markdown(arxiv_paper["abstract"])
        if "judgement" in arxiv_paper:
            st.markdown(arxiv_paper["judgement"])
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
        merged_paper_list = merge_dicts(paper_lists)
        info_text = f"✅ Done obtaining {len(merged_paper_list)} papers"
        st.write(info_text)
        status.update(label=info_text, state="complete", expanded=False)
    # temp_merged_paper_list = {}
    # for paper_id, paper in merged_paper_list.items():
    #     temp_merged_paper_list[paper_id] = paper
    #     if len(temp_merged_paper_list) > 5:
    #         break
    # return temp_merged_paper_list
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
                print(papers_by_topics[topic])
    st.session_state["papers_by_topics"] = papers_by_topics


def llm_read_papers(paper_list):
    with st.status("Reading papers", expanded=False) as status:
        with open("./data/2024-09-13.resp.json") as f:
            judgement_results = {}
            for line in f:
                paper = json.loads(line)
                judgement_results[paper["id"]] = paper["judgement"]
        info_text = f"🔄 Read {len(judgement_results)} papers"
        status.update(label=info_text, state="running")

    for paper_id in paper_list.keys():
        paper_judgement = judgement_results[paper_id]
        paper_list[paper_id]["judgement"] = paper_judgement

    classify_papers(paper_list)


# Sidebar
st.sidebar.title("arXiv digest")

if st.sidebar.button("Fetch new papers"):
    st.session_state["arxiv_papers"] = fetch_arxiv_papers(config)

if st.sidebar.button("Read papers"):
    llm_read_papers(st.session_state["arxiv_papers"])

# Define selected_topic before using it
selected_topic = st.sidebar.radio(
    "Select Topic",
    list(st.session_state.get("papers_by_topics", {}).keys()),
    index=0,
)

if "papers_by_topics" in st.session_state:
    display_papers(selected_topic, st.session_state["papers_by_topics"][selected_topic])
