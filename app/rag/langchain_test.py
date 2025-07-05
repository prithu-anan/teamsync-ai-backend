from langchain_google_genai import ChatGoogleGenerativeAI
import os
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import SecretStr

# print("google api key is", os.getenv("GEMINI_API_KEY"))

# messages = [
#     SystemMessage(content="Solve the following math problems"),
#     HumanMessage(content="What is 81 divided by 9?"),
# ]


# ---- LangChain OpenAI Chat Model Example ----

# # Create a ChatOpenAI model
# model = ChatOpenAI(model="gpt-4o")

# # Invoke the model with messages
# result = model.invoke(messages)
# print(f"Answer from OpenAI: {result.content}")


# ---- Anthropic Chat Model Example ----

# Create a Anthropic model
# Anthropic models: https://docs.anthropic.com/en/docs/models-overview
# model = ChatAnthropic(model="claude-3-opus-20240229")

# result = model.invoke(messages)
# print(f"Answer from Anthropic: {result.content}")


# ---- Google Chat Model Example ----

# https://console.cloud.google.com/gen-app-builder/engines
# https://ai.google.dev/gemini-api/docs/models/gemini
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    client_options=None,
    transport=None,
    additional_headers=None,
    client=None,
    api_key=SecretStr(os.getenv("GEMINI_API_KEY") or "") if os.getenv("GEMINI_API_KEY") else None,
    temperature=0.0,
    max_tokens=1000,
    top_p=1,
    top_k=40
)

# result = model.invoke(messages)
# print(f"Answer from Google: {result.content}")
