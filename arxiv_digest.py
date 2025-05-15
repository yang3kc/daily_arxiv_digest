import streamlit as st
import json
from src.rss import ArxivRSS
from src.llm import LLMPaperReader
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
        full_paper_list = pd.concat(paper_lists)
        info_text = f"✅ Done obtaining {len(full_paper_list)} papers"
        st.write(info_text)
        status.update(label=info_text, state="complete", expanded=False)
    st.session_state["arxiv_papers"] = full_paper_list


def llm_read_papers():
    paper_list = st.session_state["arxiv_papers"]
    llm_reader = LLMPaperReader(
        config["openai_model"], config["topics"], config["timeout_seconds"]
    )

    paper_dict_list = paper_list.to_dict(orient="records")
    paper_judgements = llm_reader.read_papers(
        paper_dict_list, config["number_of_concurrent_tasks"]
    )
    st.session_state["paper_judgements"] = paper_judgements


def merge_paper_list_with_paper_judgements():
    paper_list = st.session_state["arxiv_papers"]
    paper_judgements = st.session_state["paper_judgements"]

    paper_list_with_judgement = paper_list.merge(paper_judgements, on="id", how="left")
    paper_list_with_judgement["relevance"] = paper_list_with_judgement[
        "relevance"
    ].fillna(0)
    paper_list_with_judgement["reason"] = paper_list_with_judgement["reason"].fillna("")

    st.session_state["papers_with_judgement"] = paper_list_with_judgement


# Sidebar
st.sidebar.title("arXiv digest")

if st.sidebar.button("Fetch new papers"):
    fetch_arxiv_papers(config)


if st.sidebar.button("Read papers"):
    llm_read_papers()
    merge_paper_list_with_paper_judgements()

threshold = st.sidebar.slider(
    "Relevance threshold",
    min_value=0.0,
    max_value=1.0,
    value=0.7,
    step=0.1,
    help="Papers with relevance scores above this threshold will be shown",
)
st.session_state["threshold"] = threshold

# Define selected_topic before using it

if "papers_with_judgement" in st.session_state:
    selected_topic = st.sidebar.radio(
        "Select Topic",
        list(st.session_state["papers_with_judgement"].topic.unique()),
        index=0,
    )

    display_papers(selected_topic)
