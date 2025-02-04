from openai import AsyncOpenAI
import asyncio
import json
import streamlit as st


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

    def __init__(self, model, topics, timeout_seconds):
        self.model = model
        self.topics = topics
        self.timeout_seconds = timeout_seconds
        self.client = AsyncOpenAI()

    # The code is borrowed from https://gist.github.com/benfasoli/650a57923ab1951e1cb6355f033cbc8b
    def _limit_concurrency(self, tasks, number_of_concurrent_tasks):
        """
        Decorate coroutines to limit concurrency.
        Enforces a limit on the number of coroutines that can run concurrently in higher level asyncio-compatible concurrency managers like asyncio.gather(coroutines)
        """
        semaphore = asyncio.Semaphore(number_of_concurrent_tasks)

        async def with_concurrency_limit(task):
            async with semaphore:
                return await task

        return [with_concurrency_limit(task) for task in tasks]

    async def read_paper(self, paper):
        print(f"Reading paper: [[{paper['title']}]]")
        try:
            response = await asyncio.wait_for(
                self._call_api(paper), timeout=self.timeout_seconds
            )
            response_content = response.choices[0].message.content
            response_json = json.loads(response_content)
            judgement = {"id": paper["id"], "judgement": response_json}
            print(f"Done reading paper: [[{paper['title']}]]")
            return judgement
        except asyncio.TimeoutError:
            print(f"Timeout reading paper: [[{paper['title']}]]")
            return {"id": paper["id"], "judgement": None, "error": "timeout"}
        except Exception as e:
            print(f"Error reading paper: [[{paper['title']}]]: {str(e)}")
            return {"id": paper["id"], "judgement": None, "error": str(e)}

    async def read_papers(self, papers, number_of_concurrent_tasks=10):
        tasks = [self.read_paper(paper) for paper in papers]
        total_papers = len(papers)
        completed_tasks = 0

        # Initialize progress tracking elements in session state if they don't exist
        if "progress_bar" not in st.session_state:
            st.session_state.progress_bar = st.progress(0)
        if "progress_text" not in st.session_state:
            st.session_state.progress_text = st.empty()

        async def process_paper(task, index):
            nonlocal completed_tasks
            result = await task
            # Update progress bar and text
            completed_tasks += 1
            progress = completed_tasks / total_papers
            st.session_state.progress_bar.progress(progress)
            st.session_state.progress_text.text(
                f"Processed {completed_tasks}/{total_papers} papers"
            )
            return result

        limited_tasks = self._limit_concurrency(
            [process_paper(task, i) for i, task in enumerate(tasks)],
            number_of_concurrent_tasks,
        )

        responses = await asyncio.gather(*limited_tasks, return_exceptions=True)

        # Clear the progress text
        st.session_state.progress_text.empty()

        return responses

    async def _call_api(self, paper):
        response = await self.client.chat.completions.create(
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
