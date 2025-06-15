# app/llm/gemini_provider.py

import os
from google import generativeai as genai
from app.llm.base import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def generate(self, prompt: str, num_responses: int = 1) -> list:

        responses = []

        for _ in range(num_responses):

            response = self.model.generate_content(prompt)
            responses.append(response.text)
        return responses
