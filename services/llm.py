import os
from dotenv import load_dotenv

load_dotenv()

def get_llm_model():
    LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "azure_openai")

    if LLM_PROVIDER == "azure_openai":
        from langchain_openai import AzureChatOpenAI
        model = AzureChatOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
            openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
            temperature=0,
        )
    elif LLM_PROVIDER == "ollama":
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