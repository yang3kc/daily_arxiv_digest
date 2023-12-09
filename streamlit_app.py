import streamlit as st
import pandas as pd
import gzip
import json
import datetime
import os

if __name__ == "__main__":
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    temp_data_dir = "./data"

    paper_file = os.path.join(temp_data_dir, f"{date}.json.gz")
    with gzip.open(paper_file, "rb") as f:
        merged_paper_list = json.loads(f.read().decode("utf-8"))
    paper_df = pd.DataFrame.from_dict(merged_paper_list.values())

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

    for index, col in merged_df.iterrows():
        st.markdown(f"### {col['title']}")
        st.markdown(f"{col['authors']}")
        st.markdown(col["url"])
        st.markdown(f"**ChatGPT comment**")
        st.markdown(col["reason"])
        st.markdown(f"**Abstract**")
        st.markdown(col["abstract"])
