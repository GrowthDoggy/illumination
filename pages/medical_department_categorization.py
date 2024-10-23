import streamlit as st
import pandas as pd
from langchain_core.messages import SystemMessage, HumanMessage
from services.llm import get_llm_model
import logging


def match_departments(dept2, depts_sheet1):
    model = get_llm_model(max_tokens=30)

    resp = model.invoke([
        SystemMessage(content=f"""
        你将扮演医疗行业助手，负责将待匹配的科室与候选科室列表进行最合适的匹配。请基于语义理解和医学常识作出判断，分析待匹配科室与候选科室之间的相关性。

执行要求

匹配逻辑：根据科室的名称、疾病、症状等信息进行匹配，要求只能从候选科室列表选取。如果需要，可以搜索相关疾病或症状以进一步确认匹配结果。
不确定匹配：如果对某个匹配结果不够确定，选择最可能的科室，并在匹配结果后加上“（待确认）”以标识需要进一步确认的科室。
分析步骤：学习案例中的分析过程，详细分析待匹配科室的关键词，如年龄段、疾病类型等，并结合候选科室做出合理推测。
输出格式：请只要输出“匹配结果”的内容，“分析过程”部分可以隐去。

案例
待匹配科室： (0-6)岁眼保健亚专科
候选科室列表：小儿眼科、内科
分析过程：因为“(0-6)岁”表明患者为儿童，“眼保健”属于眼科领域。
匹配结果：小儿眼科

待匹配科室： (本部)痤疮门诊
候选科室列表：小儿眼科、外科、皮肤科
分析过程：痤疮属于常见皮肤病，通常由皮肤科处理。
匹配结果：皮肤科

待匹配科室： (本部)痤疮门诊
候选科室列表：小儿眼科、外科
分析过程：痤疮与皮肤科相关，但候选科室中未列出皮肤科，外科可能负责部分相关手术。
匹配结果：外科（待确认）

        """),
        HumanMessage(content=f"""
        待匹配科室：{dept2}
        候选科室列表：{', '.join(depts_sheet1)}
        匹配结果：
        """)
    ])

    reply = resp.content

    if "匹配结果：" in reply:
        reply = reply.replace("匹配结果：", "").strip()

    # 判断回复中是否包含“（待确认）”
    if "（待确认）" in reply:
        matched_dept = reply.replace("（待确认）", "").strip()
        remark = "待确认"
    else:
        matched_dept = reply
        remark = "准确"

    logging.info(f"科室名称：{dept2}，匹配结果：{matched_dept}，备注：{remark}")

    return matched_dept, remark

st.title("医疗科室分类工具")

st.header("上传 Excel 文件")

uploaded_file = st.file_uploader("上传包含多个工作表的 Excel 文件", type=["xlsx", "xls"])

if uploaded_file:
    # 获取 Excel 文件对象
    excel_file = pd.ExcelFile(uploaded_file)

    # 获取所有工作表名称
    sheet_names = excel_file.sheet_names

    # 选择要处理的两个工作表
    sheet1_name = st.selectbox("选择第一个工作表（表1）", sheet_names, key='sheet1')
    sheet2_name = st.selectbox("选择第二个工作表（表2）", sheet_names, key='sheet2')

    # 读取用户选择的工作表
    df_sheet1 = pd.read_excel(uploaded_file, sheet_name=sheet1_name)
    df_sheet2 = pd.read_excel(uploaded_file, sheet_name=sheet2_name)

    st.subheader(f"{sheet1_name} 前 10 行预览")
    st.write(df_sheet1.head(10))

    st.subheader(f"{sheet2_name} 前 10 行预览")
    st.write(df_sheet2.head(10))

    # 从表1中选择科室名称列
    column_sheet1 = st.selectbox(f"选择 {sheet1_name} 中的科室名称列", df_sheet1.columns, key='column_sheet1')

    # 从表2中选择科室名称列
    column_sheet2 = st.selectbox(f"选择 {sheet2_name} 中的科室名称列", df_sheet2.columns, key='column_sheet2')

    if st.button("开始匹配"):
        with st.spinner('正在匹配，请稍候...'):
            # 获取科室名称列表
            depts_sheet1 = df_sheet1[column_sheet1].astype(str).tolist()
            depts_sheet2 = df_sheet2[column_sheet2].astype(str).tolist()

            results = []
            for idx, dept2 in enumerate(depts_sheet2):
                matched_dept1, remark = match_departments(dept2, depts_sheet1)
                results.append({
                    "序号": idx + 1,
                    f"表2 ({sheet2_name})": dept2,
                    f"表1 ({sheet1_name})": matched_dept1,
                    "备注": remark
                })

            result_df = pd.DataFrame(results)

            st.subheader("匹配结果预览")
            st.write(result_df.head(10))


            # 提供下载
            def convert_df_to_excel(df):
                from io import BytesIO
                output = BytesIO()
                writer = pd.ExcelWriter(output, engine='xlsxwriter')
                df.to_excel(writer, index=False)
                writer.close()
                processed_data = output.getvalue()
                return processed_data


            excel_data = convert_df_to_excel(result_df)

            st.download_button(
                label="下载匹配结果",
                data=excel_data,
                file_name="匹配结果.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
