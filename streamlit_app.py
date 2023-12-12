import streamlit as st
import pandas as pd
import gzip
import json
import datetime
import os
import re


def remove_parentheses_content(s):
    return re.sub(r"\([^)]*\)", "", s)


if __name__ == "__main__":
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    temp_data_dir = "./data"

    # Load paper information
    paper_file = os.path.join(temp_data_dir, f"{date}.json.gz")
    with gzip.open(paper_file, "rb") as f:
        merged_paper_list = json.loads(f.read().decode("utf-8"))
    paper_df = pd.DataFrame.from_dict(merged_paper_list.values())

    # Load judgement
    judgement_file = os.path.join(temp_data_dir, f"{date}.resp.json")
    juedement_list = []
    with open(judgement_file) as f:
        for line in f:
            paper = json.loads(line)
            juedement_list.append(paper)

    paper_worth_reading = []
    for judgement in juedement_list:
        paper_id = judgement["id"]
        score_reason = []
        for topic, value in judgement["judgement"].items():
            if value["relevance"] > 0.8:
                score_reason.append(
                    f"<{value['relevance']}> - <{topic}>: {value['reason']}"
                )
        if score_reason:
            paper = {"id": judgement["id"], "reason": " || ".join(score_reason)}
            paper_worth_reading.append(paper)

    paper_worth_reading_df = pd.DataFrame.from_dict(paper_worth_reading)

    merged_df = pd.merge(paper_df, paper_worth_reading_df, on="id")
    other_papers_df = paper_df[~paper_df["id"].isin(merged_df["id"])]
    reason_other_papers = []
    for index, col in other_papers_df.iterrows():
        for judgement in juedement_list:
            if col["id"] == judgement["id"]:
                score_reason = []
                for topic, value in judgement["judgement"].items():
                    score_reason.append(
                        f"<{value['relevance']}> - <{topic}>: {value['reason']}"
                    )
                reason_other_papers.append(" || ".join(score_reason))
    other_papers_df["reason"] = reason_other_papers

    st.title(f"Arxiv paper digest on {date}")
    tab1, tab2 = st.tabs(
        [
            f"Paper Worth Reading ({len(merged_df)})",
            f"Paper Not Worth Reading ({len(other_papers_df)})",
        ]
    )
    for tab, df in zip([tab1, tab2], [merged_df, other_papers_df]):
        with tab:
            for index, col in df.iterrows():
                st.markdown(
                    f"### [{remove_parentheses_content(col['title'])}]({col['url']})"
                )
                reasons = col["reason"].split(" || ")
                for reason in reasons:
                    st.markdown(reason)
                st.markdown(f"{col['authors']}")

                with st.expander("Abstract"):
                    st.markdown(col["abstract"])

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
