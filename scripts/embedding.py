import os
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

loader = CSVLoader(
    file_path="../files/hospital_departments_full.csv",
    csv_args={
            "delimiter": ",",
            "fieldnames": ["一级科室", "二级科室", "科室简介"],
        },
    )
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)

connection = os.getenv("DATABASE_URL")
collection_name = "hospital_departments"
vectorstore = PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=connection,
    use_jsonb=True,
)

retriever = vectorstore.as_retriever()

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

