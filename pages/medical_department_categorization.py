import streamlit as st
import pandas as pd
from langchain_core.messages import SystemMessage, HumanMessage
from services.llm import get_llm_model


def classify_text(text, categories):
    model = get_llm_model()
    categories_string = "、".join(categories)
    resp = model.invoke([
        SystemMessage(content=f"""
    你是一名医疗科室分类助手。
    请根据以下分类类别，判断给定的科室文本属于哪个类别。如果你认为不属于任何类别，请回答“未分类”。你需要严格按照给定的分类类别回答，不能自行添加类别。
    
    案例 1：
    科室文本：心血管内科
    分类类别：内科、外科、妇产科、儿科
    回答：内科
    
    案例 2：
    科室文本：心理咨询科
    分类类别：内科、外科、妇产科、儿科
    回答：未分类
    
    案例 3：
    科室文本：心理咨询科
    分类类别：内科、外科、妇产科、儿科、心理科
    回答：心理科
    
    请仅回答给定的分类类别，不需要任何解释。
    
    """),
        HumanMessage(content=f"""
    科室文本：{text}
    分类类别：{categories_string}
    回答：
    """)
    ])

    result = resp.content
    print(f"文本: {text}，分类类别：{categories_string}，检测结果: {result}")

    return result

st.title("医疗科室分类工具")

st.header("上传 Excel 文件")
# 上传 Excel 1
uploaded_file1 = st.file_uploader("上传包含科室名称的 Excel 文件", type=["xlsx", "xls"], key="file1")

# 上传 Excel 2
uploaded_file2 = st.file_uploader("上传候选科室分类的 Excel 文件", type=["xlsx", "xls"], key="file2")

if uploaded_file1 and uploaded_file2:
    df1 = pd.read_excel(uploaded_file1)
    df2 = pd.read_excel(uploaded_file2)

    st.subheader("Excel 1 前 10 行预览")
    st.write(df1.head(10))

    st.subheader("Excel 2 前 10 行预览")
    st.write(df2.head(10))

    st.subheader("数据处理")

    # 从 Excel 1 中选择一列作为待分类数据
    column1 = st.selectbox("选择 Excel 1 中的待分类列", df1.columns)

    # 从 Excel 2 中选择一列作为分类类别
    column2 = st.selectbox("选择 Excel 2 中的分类类别列", df2.columns)

    if st.button("开始分类"):
        categories = df2[column2].astype(str).unique().tolist()
        df1['分类结果'] = df1[column1].astype(str).apply(lambda x: classify_text(x, categories))

        st.subheader("分类结果预览")
        st.write(df1.head(10))


        # 提供下载
        # @st.cache_data
        def convert_df_to_excel(df):
            from io import BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            processed_data = output.getvalue()
            return processed_data


        excel_data = convert_df_to_excel(df1)

        st.download_button(
            label="下载分类结果",
            data=excel_data,
            file_name="分类结果.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )