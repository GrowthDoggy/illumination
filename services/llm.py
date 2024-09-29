import os
from dotenv import load_dotenv

load_dotenv()

def get_llm_model():
    LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "azure_openai")

    if LLM_PROVIDER == "azure_openai":
        from langchain_openai import AzureChatOpenAI
        model = AzureChatOpenAI(
            openai_api_base=os.environ["AZURE_OPENAI_ENDPOINT"],
            deployment_name=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
            openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
            openai_api_key=os.environ["AZURE_OPENAI_API_KEY"],
            openai_api_type="azure",
            temperature=0,
        )
    elif LLM_PROVIDER == "ollama":
        from langchain_ollama import ChatOllama

        model = ChatOllama(
            base_url="http://localhost:11434",
            model="llama3.1",
            temperature=0,
        )
    else:
        raise ValueError("Unsupported LLM_PROVIDER value.")

    return model