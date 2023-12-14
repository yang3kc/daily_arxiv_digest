from openai import OpenAI
import json


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
        The output should be in JSON format and follow the following schema:
        --------------
        ```json
        {{
            'topic 1': {{
                'relevance': 0,
                'reason': ''
            }},
            'topic 2': {{
                'relevance': 0.9,
                'reason': 'The paper ....'
            }}
        }}
         ```
    """

    def __init__(self, model, topics):
        self.model = model
        self.topics = topics
        self.client = OpenAI()

    def read_paper(self, paper):
        response = self._call_api(paper)
        response_content = response.choices[0].message.content
        response_json = json.loads(response_content)
        return response_json

    def _call_api(self, paper):
        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": self.system_message},
                {
                    "role": "user",
                    "content": self.user_message.format(
                        title=paper["title"],
                        abstract=paper["abstract"],
                        topics=self.topics,
                    ),
                },
            ],
        )
        return response
