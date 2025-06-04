import streamlit as st
import json
from src.rss import ArxivRSS
from src.llm import LLMPaperReader
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

########################################################
# Load config
with open("./config.json") as f:
    config = json.load(f)


########################################################
# Data functions
########################################################
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
        full_paper_list.drop_duplicates(subset=["id"], inplace=True)
        info_text = f"✅ Done obtaining {len(full_paper_list)} papers"
        st.write(info_text)
        status.update(label=info_text, state="complete", expanded=False)
    st.session_state["arxiv_papers"] = full_paper_list


def llm_read_papers():
    llm_reader = LLMPaperReader(
        config["openai_model"], config["topics"], config["timeout_seconds"]
    )

    paper_list = st.session_state["arxiv_papers"]
    paper_dict_list = paper_list.to_dict(orient="records")

    if "progress_bar" not in st.session_state:
        st.session_state.progress_bar = st.progress(0)
    if "progress_text" not in st.session_state:
        st.session_state.progress_text = st.empty()

    paper_judgements_list = []
    with ThreadPoolExecutor(
        max_workers=config["number_of_concurrent_tasks"]
    ) as executor:
        futures = [
            executor.submit(llm_reader.read_paper, paper_dict)
            for paper_dict in paper_dict_list
        ]
        for future in as_completed(futures):
            try:
                paper_judgements_list.append(future.result())
            except Exception as e:
                st.warning(f"Worker failed: {e}")
            progress = len(paper_judgements_list) / len(paper_dict_list)
            st.session_state.progress_bar.progress(progress)
            st.session_state.progress_text.text(
                f"Processed {len(paper_judgements_list)}/{len(paper_dict_list)} papers"
            )
    paper_judgements_df = pd.concat(paper_judgements_list)
    paper_judgements_df.drop_duplicates()

    st.session_state.progress_text.empty()

    st.session_state["paper_judgements"] = paper_judgements_df


def merge_paper_list_with_paper_judgements():
    paper_list = st.session_state["arxiv_papers"]
    paper_judgements = st.session_state["paper_judgements"]

    paper_list_with_judgement = paper_list.merge(paper_judgements, on="id", how="left")
    paper_list_with_judgement["relevance"] = paper_list_with_judgement[
        "relevance"
    ].fillna(0)
    paper_list_with_judgement["reason"] = paper_list_with_judgement["reason"].fillna("")

    st.session_state["papers_with_judgement"] = paper_list_with_judgement


########################################################
# UI functions
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


########################################################
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

if "papers_with_judgement" in st.session_state:
    selected_topic = st.sidebar.radio(
        "Select Topic",
        list(st.session_state["papers_with_judgement"].topic.unique()),
        index=0,
    )

    display_papers(selected_topic)
