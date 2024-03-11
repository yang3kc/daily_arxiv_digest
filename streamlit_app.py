import streamlit as st
import pandas as pd
import gzip
import json
import datetime
import os
import re


temp_data_dir = "./data"


def remove_parentheses_content(s):
    return re.sub(r"\([^)]*\)", "", s)


def load_latest_date():
    list_of_files = os.listdir(temp_data_dir)
    file_date_list = []
    for file in list_of_files:
        if file.endswith(".json"):
            date = file.split(".")[0]
            file_date_list.append(date)
    return max(file_date_list)


if __name__ == "__main__":
    date = load_latest_date()

    # Load judgement
    judgement_file = os.path.join(temp_data_dir, f"{date}.resp.json")
    judgement_results = {}
    with open(judgement_file) as f:
        for line in f:
            paper = json.loads(line)
            judgement_results[paper["id"]] = paper["judgement"]

    # Load paper information
    paper_file = os.path.join(temp_data_dir, f"{date}.json.gz")
    with gzip.open(paper_file, "rb") as f:
        paper_dict = json.loads(f.read().decode("utf-8"))

    # Combine the paper info and judgement
    for paper_id in paper_dict.keys():
        paper_judgement = judgement_results[paper_id]
        paper_dict[paper_id]["judgement"] = paper_judgement
        paper_dict[paper_id]["title"] = remove_parentheses_content(
            paper_dict[paper_id]["title"]
        )

    relevance_threshold = 0.8

    # Find relevant papers
    relevant_papers = {}
    relevant_paper_ids = set()
    for id, paper_info in paper_dict.items():
        for topic, relevance in paper_info["judgement"].items():
            if relevance["relevance"] > relevance_threshold:
                relevant_paper_ids.add(id)
                temp_obj = {"paper_id": id, "relevance": relevance}
                if topic in relevant_papers:
                    relevant_papers[topic].append(temp_obj)
                else:
                    relevant_papers[topic] = [temp_obj]

    st.title(f"Arxiv paper digest on {date}")
    relevant_paper_tab, irrelevant_paper_tab = st.tabs(
        [
            f"Relevant papers ({len(relevant_paper_ids)})",
            f"Irrelevant papers ({len(paper_dict) - len(relevant_paper_ids)})",
        ]
    )

    with relevant_paper_tab:
        for topic, papers in relevant_papers.items():
            st.markdown(f"# {topic}")
            for paper in papers:
                paper_title = paper_dict[paper["paper_id"]]["title"]
                paper_url = paper_dict[paper["paper_id"]]["url"]
                st.markdown(f"### [{paper_title}]({paper_url})")
                st.markdown(
                    f"{paper['relevance']['relevance']} || {paper['relevance']['reason']}"
                )
                st.markdown(f"{', '.join(paper_dict[paper['paper_id']]['authors'])}")
                with st.expander("Abstract"):
                    st.markdown(paper_dict[paper["paper_id"]]["abstract"])

    with irrelevant_paper_tab:
        for id, paper_info in paper_dict.items():
            if id not in relevant_paper_ids:
                paper_title = paper_info["title"]
                paper_url = paper_info["url"]
                st.markdown(f"### [{paper_title}]({paper_url})")
                for topic, relevance in paper_info["judgement"].items():
                    if relevance["relevance"] > 0:
                        st.markdown(
                            f"{relevance['relevance']} || {topic} || {relevance['reason']}"
                        )
                st.markdown(f"{', '.join(paper_info['authors'])}")
                with st.expander("Abstract"):
                    st.markdown(paper_info["abstract"])

    # tab1, tab2 = st.tabs(
    #     [
    #         f"Paper Worth Reading ({len(merged_df)})",
    #         f"Paper Not Worth Reading ({len(other_papers_df)})",
    #     ]
    # )
    # for tab, df in zip([tab1, tab2], [merged_df, other_papers_df]):
    #     with tab:
    #         for index, col in df.iterrows():
    #             st.markdown(
    #                 f"### [{remove_parentheses_content(col['title'])}]({col['url']})"
    #             )
    #             reasons = col["reason"].split(" || ")
    #             for reason in reasons:
    #                 st.markdown(reason)
    #             st.markdown(f"{col['authors']}")

    #             with st.expander("Abstract"):
    #                 st.markdown(col["abstract"])

    # with tab2:
    #     st.markdown(f"# Paper Not Worth Reading for {date}")
    #     for index, col in other_papers_df.iterrows():
    #         st.markdown(f"### {col['title']}")
    #         st.markdown(f"{col['authors']}")
    #         st.markdown(col["url"])
    #         st.markdown(f"**ChatGPT comment**")
    #         st.markdown(col["reason"])
    #         st.markdown(f"**Abstract**")
    #         st.markdown(col["abstract"])
