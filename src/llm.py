from openai import OpenAI, OpenAIError
from pydantic import BaseModel, Field
from typing import List
import os
import pandas as pd


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
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"), timeout=timeout_seconds
        )
        self.model = model
        self.topics = topics

    def read_paper(self, paper, max_retries: int = 3):
        """Read a single paper and return a judgement dataframe.

        A few requests to the OpenAI API may fail temporarily (e.g. returning a
        404 status).  To prevent a single failure from aborting the whole batch
        run, this method retries the request a few times and falls back to a
        neutral judgement when all retries fail.
        """

        attempt = 0
        while attempt < max_retries:
            try:
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
            except OpenAIError as e:
                attempt += 1
                if attempt >= max_retries:
                    # Construct a neutral judgement so downstream code keeps running
                    topics = self.topics
                    if not isinstance(topics, list):
                        topics = [topics]
                    paper_judgement_df = pd.DataFrame(
                        [{"topic": t, "relevance": 0.0, "reason": str(e)} for t in topics]
                    )
                    paper_judgement_df["id"] = paper["id"]
                    return paper_judgement_df
