import os
from dotenv import load_dotenv

load_dotenv()

def get_llm_model():
    llm_provider = os.environ.get("LLM_PROVIDER", "azure_openai")

    if llm_provider == "azure_openai":
        from langchain_openai import AzureChatOpenAI
        model = AzureChatOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
            openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
            temperature=0,
        )
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

        model = ChatOpenAI(**openai_params)
    elif llm_provider == "ollama":
        from langchain_ollama import ChatOllama

        model = ChatOllama(
            base_url=os.environ["OLLAMA_API_ENDPOINT"],
            model=os.environ["OLLAMA_MODEL"],
            temperature=0,
            top_k=10,
            top_p=0.1,
        )
    else:
        raise ValueError("Unsupported LLM_PROVIDER value.")

    return model