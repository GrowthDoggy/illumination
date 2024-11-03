from langchain_community.document_loaders import PyPDFLoader

# Load the document
file_path = "../files/人保e相助_2024_4-41.pdf"
loader = PyPDFLoader(file_path)

docs = loader.load()

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o")


from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)
vectorstore = InMemoryVectorStore.from_documents(
    documents=splits, embedding=OpenAIEmbeddings(model="text-embedding-3-small")
)

retriever = vectorstore.as_retriever()

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know."
    "\n\n"
    "{context}"
)


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

results = rag_chain.invoke({"input": "请解析附件中的合同条款，按照以下规则处理完毕后，直接输出结果。从「7.18 重大疾病」中，提取序号（1）至（101）的序号和疾病名称。请注意，所有序号和疾病名称请完整显示，不要做任何省略处理。"})

for doc in results['context']:
    print("RAG 的上下文", doc)
# print("RAG 的上下文", results['context'])
print("回答", results['answer'])