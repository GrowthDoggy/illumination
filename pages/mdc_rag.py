import os
import streamlit as st
import pandas as pd
from langchain_core.messages import SystemMessage, HumanMessage
from services.llm import get_llm_model
import logging
from langchain import hub
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector

# Prepare the embeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

prompt = hub.pull("rlm/rag-prompt")

connection = os.getenv("DATABASE_URL")
collection_name = "hospital_departments"
vectorstore = PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=connection,
    use_jsonb=True,
)

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6})


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger()

def match_departments(dept_physical_level2, dept_physical_level1, dept_intro, candidate_departments, retriever):
    # 构建查询
    query = f"二级科室：{dept_physical_level2}，科室简介：{dept_intro}"

    # 检索相关文档
    retrieved_docs = retriever.get_relevant_documents(query)

    # 格式化检索到的文档作为上下文
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    model = get_llm_model(max_tokens=200)

    logger.info(f"RAG 过程中查询到的上下文: {context}")

    resp = model.invoke([
        SystemMessage(content=f"""
你将扮演医疗行业助手，负责将待匹配的科室与候选科室列表进行最合适的匹配。请基于提供的一级科室、科室简介、语义理解、医学常识作出判断，分析待匹配科室与候选科室之间的相关性，按照相关性高低排列输出 1 个或者多个匹配结果。请仅从参考文档的二级科室以及候选科室列表中挑选科室，不能匹配出参考文档和候选科室列表中不存在的科室。
如果参考文档中有匹配的二级科室，它们的优先级最高。

参考文档：
{context}

执行要求：
1. 匹配逻辑：根据科室的一级科室、科室简介、名称、疾病、症状等信息进行匹配。如果需要，可以搜索相关疾病或症状以进一步确认匹配结果。
2. 分析步骤：可以参考分析过程的思路并且一步步地进行分析，详细分析待匹配科室和背景中提到的关键词，如年龄段、疾病类型等，并结合候选科室做出合理推测。
3. 输出格式：请只要输出“匹配结果”的内容，“分析过程”部分可以隐去。

案例
参考文档：
- 一级科室: 内科
- 二级科室: 神经内科

- 待匹配科室： 炎性肌病多学科联合门诊
- 待匹配科室的一级科室：多学科联合门诊(MDT)
- 待匹配科室的简介：我院炎性肌病多学科联合门诊由风湿免疫科神经内科、心血管内科、病理科、呼吸内科等五个相关科室医生组成
- 候选科室列表：风湿免疫科、神经内科、心血管内科、呼吸内科、病理科、皮肤科、感染科、内分泌科
- 匹配结果：神经内科、风湿免疫科、心血管内科、呼吸内科、病理科、皮肤科、感染科、内分泌科
        """),
        HumanMessage(content=f"""
- 待匹配科室：{dept_physical_level2}
- 待匹配科室的一级科室：{dept_physical_level1}
- 待匹配科室的简介：{dept_intro if pd.notna(dept_intro) and dept_intro and dept_intro != 'nan' else "无"}
- 候选科室列表：{', '.join(candidate_departments)}
- 匹配结果：
        """)
    ])

    reply = resp.content

    logger.info(f"科室名称: {dept_physical_level2}, 一级科室名称：{dept_physical_level1}, 简介：{dept_intro}, 科室候选：{candidate_departments}, 匹配结果: {reply}")

    return reply

st.title("医疗科室分类工具")

st.header("上传 Excel 文件")

uploaded_file = st.file_uploader("上传包含两个工作表的 Excel 文件", type=["xlsx", "xls"])

if uploaded_file:
    # 获取 Excel 文件对象
    excel_file = pd.ExcelFile(uploaded_file)

    # 获取所有工作表名称
    sheet_names = excel_file.sheet_names

    # 选择工作表
    sheet1_name = st.selectbox("选择候选科室列表所在的工作表（Sheet 1）", sheet_names, key='sheet1')
    remaining_sheet_names = [name for name in sheet_names if name != sheet1_name]
    sheet2_name = st.selectbox("选择需要匹配的工作表（Sheet 2）", remaining_sheet_names, key='sheet2')

    # 读取工作表
    df_sheet1 = pd.read_excel(uploaded_file, sheet_name=sheet1_name)
    df_sheet2 = pd.read_excel(uploaded_file, sheet_name=sheet2_name)

    st.subheader(f"{sheet1_name} 前 10 行预览")
    st.write(df_sheet1.head(10))

    st.subheader(f"{sheet2_name} 前 10 行预览")
    st.write(df_sheet2.head(10))

    # 定义所需的列名
    required_columns_sheet1 = ['二级科室']  # Sheet1 中需要的列名
    required_columns_sheet2 = ['二级科室（物理科室）', '一级科室（物理科室）', '科室简介（物理科室）']  # Sheet2 中需要的列名

    # 检查 Sheet1 是否包含所需的列
    missing_columns_sheet1 = [col for col in required_columns_sheet1 if col not in df_sheet1.columns]

    # 检查 Sheet2 是否包含所需的列
    missing_columns_sheet2 = [col for col in required_columns_sheet2 if col not in df_sheet2.columns]

    if missing_columns_sheet1 or missing_columns_sheet2:
        error_message = ''
        if missing_columns_sheet1:
            error_message += f"工作表 {sheet1_name} 缺少以下列名：{', '.join(missing_columns_sheet1)}\n"
        if missing_columns_sheet2:
            error_message += f"工作表 {sheet2_name} 缺少以下列名：{', '.join(missing_columns_sheet2)}"
        st.error(error_message)
    else:
        # 所有列名都匹配，继续处理
        # 获取列名
        column_candidate_depts = required_columns_sheet1[0]
        column_physical_level2 = required_columns_sheet2[0]
        column_physical_level1 = required_columns_sheet2[1]
        column_intro = required_columns_sheet2[2]

        if st.button("开始匹配"):
            with st.spinner('正在匹配，请稍候...'):
                # 获取候选科室列表
                candidate_departments = df_sheet1[column_candidate_depts].dropna().astype(str).unique().tolist()

                # 初始化结果列表
                results = []

                # 遍历 Sheet 2 的每一行
                for idx, row in df_sheet2.iterrows():
                    dept_physical_level2 = str(row[column_physical_level2])
                    dept_physical_level1 = str(row[column_physical_level1])
                    dept_intro = str(row[column_intro])

                    matched_depts = match_departments(dept_physical_level2, dept_physical_level1, dept_intro,
                                                      candidate_departments, retriever)

                    results.append(matched_depts)

                # 将匹配结果添加到 DataFrame
                df_sheet2['二级科室（标准科室）'] = results

                st.subheader("匹配结果预览")
                st.write(df_sheet2.head(10))


                # 提供下载
                def convert_df_to_excel(df):
                    from io import BytesIO
                    output = BytesIO()
                    writer = pd.ExcelWriter(output, engine='xlsxwriter')
                    df.to_excel(writer, index=False, sheet_name=sheet2_name)
                    writer.close()
                    processed_data = output.getvalue()
                    return processed_data


                excel_data = convert_df_to_excel(df_sheet2)

                st.download_button(
                    label="下载匹配结果",
                    data=excel_data,
                    file_name="匹配结果.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
