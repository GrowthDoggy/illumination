from langchain_community.document_loaders import PyPDFLoader

# Load the document
file_path = "../files/人保e相助_2024_4-41.pdf"
documents = PyPDFLoader(file_path).load()

# 假设我们只需要处理重疾险的第 18 到 33 页
relevant_pages = documents[17:33]  # 注意索引从 0 开始

# 创建 LLM 实例
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)

from langchain.prompts import PromptTemplate
# 定义提取疾病名称的 Prompt
prompt = PromptTemplate(
    input_variables=["chunk"],
    template="从以下内容提取序号和疾病名称，序号在（）中，疾病名称紧随其后。请精准逐字提取，不要遗漏或者自我发挥。"
             "举例："
             "(1)恶性肿瘤——重度"
             "(2)较重急性心肌梗死"
             "内容："
             "\n{chunk}\n\n"
             "提取序号和疾病名称："
)

# 从文档中提取重疾险的内容
from langchain_core.output_parsers import StrOutputParser
# 创建 LLMChain 实例
chain = prompt | llm | StrOutputParser()

# 处理每个页面并提取信息
extracted_diseases = []
for page in relevant_pages:
    response = chain.invoke({"chunk": page.page_content})
    extracted_diseases.append(response)

# 合并结果
final_disease_list = "\n".join(extracted_diseases)

# 输出结果到文件
output_file_path = "../files/extracted_diseases.txt"
with open(output_file_path, 'w', encoding='utf-8') as f:
    f.write(final_disease_list)

print(f"提取的疾病名称已写入文件: {output_file_path}")