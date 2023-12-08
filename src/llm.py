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
        Based on the title and abstract, please decide if the paper pertains to one or multiple topics below:
        --------------
        {topics}
        --------------
        If the paper is VERY relevant to a topic, provide a short explanation of why. If the the paper is not relevant to any of the topics, reply False and leave the reason empty. The output should be in JSON format and follow the following schema:
        --------------
        ```json
        {{
            'paper_is_relevant': True,
            'reason': 'The paper is relevant to topic xx because ....'
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
