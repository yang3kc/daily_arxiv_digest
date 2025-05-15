from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st


class Judgement(BaseModel):
    topic: str = Field(description="The topic of the paper")
    relevance: float = Field(
        description="The relevance of the paper to the topic, a number between 0 and 1"
    )
    reason: str = Field(description="The reason for the relevance")


class Judgements(BaseModel):
    judgements: List[Judgement] = Field(
        description="A list of topics with relevance and reasoning"
    )


class LLMPaperReader:
    system_message = """
        You are an assistant to help the user decide if a paper is very relevant to the topics of interests.
        """

    user_message = """
        Please read the following paper title and abstract:
        --------------
        Title: {title}
        Abstract: {abstract}
        --------------
        Based on the title and abstract, please rate the direct relevance of the paper with the following topics:
        --------------
        {topics}
        --------------
        For each topic, rate the relevance as a number between 0 and 1, where 0 means not relevant and 1 means very relevant.
        The paper MUST directly mention the topics to be relevant; papers with indirect relations and potential implications should have scores close to 0.
        If the paper is relevant to the topic, provide a short explanation; otherwise, leave the explanation empty.
        Use your best guess when you are not sure.
    """

    def __init__(self, model, topics, timeout_seconds):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.topics = topics
        self.timeout_seconds = timeout_seconds

    def _read_paper(self, paper):
        response = self.client.responses.parse(
            model=self.model,
            temperature=0.0,
            instructions=self.system_message,
            input=self.user_message.format(
                title=paper["title"],
                abstract=paper["abstract"],
                topics=self.topics,
            ),
            text_format=Judgements,
        )
        judgements = response.output_parsed.model_dump()["judgements"]
        paper_judgement_df = pd.DataFrame(judgements)
        paper_judgement_df["id"] = paper["id"]
        return paper_judgement_df

    def read_papers(self, papers, number_of_concurrent_tasks=10):
        paper_judgements_list = []

        if "progress_bar" not in st.session_state:
            st.session_state.progress_bar = st.progress(0)
        if "progress_text" not in st.session_state:
            st.session_state.progress_text = st.empty()

        with ThreadPoolExecutor(max_workers=number_of_concurrent_tasks) as executor:
            futures = [executor.submit(self._read_paper, paper) for paper in papers]
            finished_count = 0
            for future in as_completed(futures):
                finished_count += 1
                progress = finished_count / len(papers)
                st.session_state.progress_bar.progress(progress)
                st.session_state.progress_text.text(
                    f"Processed {finished_count}/{len(papers)} papers"
                )
                paper_judgements_list.append(future.result())
        paper_judgements_df = pd.concat(paper_judgements_list)

        # Clear the progress text
        st.session_state.progress_text.empty()

        return paper_judgements_df
