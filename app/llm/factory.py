from app.llm.deepseek_provider import DeepSeekProvider


def get_llm_provider(provider_name: str="default"):

    if provider_name == "deepseek" or provider_name == "default":
        return DeepSeekProvider()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider_name}")
