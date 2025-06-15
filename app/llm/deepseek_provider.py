from app.llm.base import BaseLLMProvider
import os
from openai import OpenAI


class DeepSeekProvider(BaseLLMProvider):

    def __init__(self):
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable not set")
        self.client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    def generate(self, prompt: str, num_responses: int = 1) -> list:

        responses = []

        for _ in range(num_responses):

            completion = self.client.chat.completions.create(
                model="deepseek/deepseek-r1-0528:free",
                messages=[{"role": "user", "content": prompt}],
            )

            responses.append(completion.choices[0].message.content)

        return responses
