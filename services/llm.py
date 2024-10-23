import os
from dotenv import load_dotenv
from typing import Any, Optional, Dict

load_dotenv()

def get_llm_model(max_tokens: Optional[int] = None, **kwargs):
    llm_provider = os.environ.get("LLM_PROVIDER", "azure_openai")

    if llm_provider == "azure_openai":
        from langchain_openai import AzureChatOpenAI

        azure_params: Dict[str, Any] = {
            "azure_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"],
            "azure_deployment": os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
            "openai_api_version": os.environ["AZURE_OPENAI_API_VERSION"],
            "temperature": 0,
        }

        if max_tokens is not None:
            azure_params["max_tokens"] = max_tokens
        azure_params.update(kwargs)

        model = AzureChatOpenAI(**azure_params)
    elif llm_provider == "openai":
        from langchain_openai import ChatOpenAI

        openai_params = {
            "model": os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo"),
            "api_key": os.environ["OPENAI_API_KEY"],
            "temperature": 0,
        }
        openai_base_url = os.environ.get("OPENAI_BASE_URL")
        if openai_base_url:
            openai_params["base_url"] = openai_base_url

        if max_tokens is not None:
            openai_params["max_tokens"] = max_tokens

        openai_params.update(kwargs)

        model = ChatOpenAI(**openai_params)
    elif llm_provider == "ollama":
        from langchain_ollama import ChatOllama

        ollama_params: Dict[str, Any] = {
            "base_url": os.environ.get("OLLAMA_API_ENDPOINT", "http://127.0.0.1:11434"),
            "model": os.environ["OLLAMA_MODEL"],
            "temperature": 0,
            "top_k": 10,
            "top_p": 0.1,
        }
        if max_tokens is not None:
            ollama_params["num_predict"] = max_tokens

        ollama_params.update(kwargs)

        model = ChatOllama(**ollama_params)
    else:
        raise ValueError("Unsupported LLM_PROVIDER value.")

    return model