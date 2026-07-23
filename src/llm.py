import os
from typing import List

import pandas as pd
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, Field

# Each provider is exposed through the OpenAI SDK: OpenRouter and Anthropic
# both offer OpenAI-compatible endpoints, so one code path serves all three.
PROVIDERS = {
    "openai": {
        "base_url": None,
        "api_key_env": "OPENAI_API_KEY",
    },
    "anthropic": {
        "base_url": "https://api.anthropic.com/v1/",
        "api_key_env": "ANTHROPIC_API_KEY",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
    },
}


def create_client(provider: str, timeout_seconds: float) -> OpenAI:
    if provider not in PROVIDERS:
        raise ValueError(
            f"Unknown provider '{provider}'; expected one of {sorted(PROVIDERS)}"
        )
    settings = PROVIDERS[provider]
    api_key = os.getenv(settings["api_key_env"])
    if not api_key:
        raise RuntimeError(
            f"Provider '{provider}' requires the {settings['api_key_env']} "
            "environment variable"
        )
    return OpenAI(
        api_key=api_key, base_url=settings["base_url"], timeout=timeout_seconds
    )


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


class Tldr(BaseModel):
    tldr: str = Field(
        description="A 2-3 sentence plain-language summary of the paper"
    )


class LLMPaperReader:
    system_message = """
        You are an assistant to help the user decide if a paper is very relevant to the topics of interests.
        """

    # The static rubric + topics come first so the shared prefix is identical
    # across every paper and providers can cache it; only the per-paper title
    # and abstract vary, and they go last.
    user_message = """
        Rate the direct relevance of a paper to each of the following topics:
        --------------
        {topics}
        --------------
        For each topic, rate the relevance as a number between 0 and 1, where 0 means not relevant and 1 means very relevant.
        Be strict and discriminating; the scores are used to select a small daily reading list, so most papers should score low on most topics:
        - 0.8-1.0: the paper's PRIMARY contribution is squarely within the topic; a researcher following this topic would consider it a must-read. Reserve 1.0 for exceptional, unambiguous matches.
        - 0.4-0.7: the paper touches the topic or uses it as context, but the topic is not its main subject.
        - 0.0-0.3: indirect relations, potential implications, or merely sharing keywords with the topic.
        If a topic description contains an exclusion (e.g. "NOT ..."), papers matching the exclusion must score 0.3 or lower on that topic.
        If the paper is relevant to the topic, provide a short explanation; otherwise, leave the explanation empty.
        Use your best guess when you are not sure.
        Now read the paper's title and abstract and rate it:
        --------------
        Title: {title}
        Abstract: {abstract}
        --------------
    """

    tldr_system_message = """
        You are a research assistant who writes concise paper summaries.
        """

    tldr_user_message = """
        Please read the following paper title and abstract:
        --------------
        Title: {title}
        Abstract: {abstract}
        --------------
        Write a 2-3 sentence TL;DR covering the key contribution, the method, and the main finding.
        Use plain language; do not repeat the title.
    """

    def __init__(self, provider, model, topics, timeout_seconds):
        self.client = create_client(provider, timeout_seconds)
        self.model = model
        self.topics = topics
        # Render the topics into a clean bulleted block once, rather than
        # stringifying the list (as a Python repr) on every scoring call. This
        # block is part of the static, cacheable prompt prefix.
        self.topics_block = self._format_topics(topics)
        # Some models (e.g. the GPT-5 family) only accept the default
        # temperature; drop the parameter permanently on the first rejection.
        self.use_temperature = True
        self.failure_count = 0

    @staticmethod
    def _format_topics(topics):
        if isinstance(topics, str):
            topics = [topics]
        return "\n".join(f"- {topic}" for topic in topics)

    def _parse_completion(self, system_message, user_message, response_model):
        kwargs = {"temperature": 0.0} if self.use_temperature else {}
        try:
            response = self.client.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                response_format=response_model,
                **kwargs,
            )
        except OpenAIError as e:
            if self.use_temperature and "temperature" in str(e):
                self.use_temperature = False
                return self._parse_completion(
                    system_message, user_message, response_model
                )
            raise
        return response.choices[0].message.parsed

    def read_paper(self, paper, max_retries: int = 3):
        """Read a single paper and return a judgement dataframe.

        A few requests to the API may fail temporarily.  To prevent a single
        failure from aborting the whole batch run, this method retries the
        request a few times and falls back to a neutral judgement when all
        retries fail.
        """

        attempt = 0
        while attempt < max_retries:
            try:
                parsed = self._parse_completion(
                    self.system_message,
                    self.user_message.format(
                        title=paper["title"],
                        abstract=paper["abstract"],
                        topics=self.topics_block,
                    ),
                    Judgements,
                )
                judgements = parsed.model_dump()["judgements"]
                paper_judgement_df = pd.DataFrame(judgements)
                paper_judgement_df["id"] = paper["id"]
                return paper_judgement_df
            except OpenAIError as e:
                attempt += 1
                if attempt >= max_retries:
                    # Construct a neutral judgement so downstream code keeps running
                    self.failure_count += 1
                    topics = self.topics
                    if not isinstance(topics, list):
                        topics = [topics]
                    paper_judgement_df = pd.DataFrame(
                        [
                            {"topic": t, "relevance": 0.0, "reason": str(e)}
                            for t in topics
                        ]
                    )
                    paper_judgement_df["id"] = paper["id"]
                    return paper_judgement_df

    def write_tldr(self, paper, max_retries: int = 3):
        """Generate a short TL;DR for a paper; empty string when all retries fail."""

        attempt = 0
        while attempt < max_retries:
            try:
                parsed = self._parse_completion(
                    self.tldr_system_message,
                    self.tldr_user_message.format(
                        title=paper["title"], abstract=paper["abstract"]
                    ),
                    Tldr,
                )
                return {"id": paper["id"], "tldr": parsed.tldr}
            except OpenAIError:
                attempt += 1
        self.failure_count += 1
        return {"id": paper["id"], "tldr": ""}
