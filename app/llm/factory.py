from app.llm.deepseek_provider import DeepSeekProvider
from app.llm.gemini_provider import GeminiProvider


def get_llm_provider(provider_name: str="default"):

    if provider_name == "deepseek" or provider_name == "default":
        return DeepSeekProvider()
    elif provider_name == "gemini":
        return GeminiProvider()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider_name}")
