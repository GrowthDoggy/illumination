import streamlit as st
import pandas as pd
from io import BytesIO
import uuid

st.title("增长汪汪 - BI 数据分析工具")

file1 = st.file_uploader("上传第一个 Excel 文件", type=["xlsx", "xls"])
file2 = st.file_uploader("上传第二个 Excel 文件", type=["xlsx", "xls"])

if file1 and file2:
    # 读取文件
    df1 = pd.read_excel(file1) if file1.name.endswith(('xlsx', 'xls')) else pd.read_csv(file1)
    df2 = pd.read_excel(file2) if file2.name.endswith(('xlsx', 'xls')) else pd.read_csv(file2)

    # 检测表头是否一致
    if df1.columns.tolist() == df2.columns.tolist():
        st.success("检测到表头一致，正在进行比较。")
        proceed_to_compare = True
    else:
        st.warning("表头不一致，请进行列映射。")
        proceed_to_compare = False

    # 如果表头不一致，让用户进行列映射
    if not proceed_to_compare:
        st.write("请选择列的对应关系（可以动态添加和删除）：")

        # 初始化映射关系列表
        if 'mappings' not in st.session_state:
            st.session_state.mappings = []

        # 按钮用于增加对应关系
        if st.button('添加对应关系'):
            new_id = str(uuid.uuid4())
            st.session_state.mappings.append({'id': new_id, 'col1': None, 'col2': None})

        # 动态生成对应关系选择框和删除按钮
        mappings = st.session_state.mappings.copy()  # 复制一份，避免迭代时修改列表
        for mapping in mappings:
            mapping_id = mapping['id']
            cols = st.columns([4, 4, 1])
            with cols[0]:
                col1 = st.selectbox(f"文件1列", df1.columns, key=f'col1_{mapping_id}')
            with cols[1]:
                col2 = st.selectbox(f"文件2列", df2.columns, key=f'col2_{mapping_id}')
            with cols[2]:
                if st.button('删除', key=f'delete_{mapping_id}'):
                    st.session_state.mappings.remove(mapping)
                    st.experimental_set_query_params()
                    st.stop()
            # 更新映射关系
            mapping['col1'] = col1
            mapping['col2'] = col2

        # 应用映射关系
        if st.button('完成映射'):
            if st.session_state.mappings:
                mapping_dict = {mapping['col2']: mapping['col1'] for mapping in st.session_state.mappings}
                df2 = df2.rename(columns=mapping_dict)
                common_columns = df1.columns.intersection(df2.columns)
                if common_columns.empty:
                    st.warning("映射后没有共同的列，无法进行比较。")
                    st.stop()
                df1 = df1[common_columns]
                df2 = df2[common_columns]
                proceed_to_compare = True
            else:
                st.warning("请至少添加一个列的对应关系。")
                st.stop()
        else:
            st.info("添加列的对应关系并点击“完成映射”按钮来进行数据比较。")
            st.stop()  # 等待用户完成映射后再继续

    if proceed_to_compare:
        # 重置索引以确保正确对齐
        df1.reset_index(drop=True, inplace=True)
        df2.reset_index(drop=True, inplace=True)

        # 比较数据，不修改原始数据，创建差异标记
        comparison_values = df1.values == df2.values
        df_all = df1.copy()
        df_all['差异'] = ''

        rows, cols = df1.shape
        for i in range(rows):
            for j in range(cols):
                if not comparison_values[i, j]:
                    df_all.iloc[i, j] = f"{df1.iloc[i, j]} --> {df2.iloc[i, j]}"
                    df_all.at[i, '差异'] = '有差异'

        # 显示前10行结果
        st.write("比较结果（前 10 行）：")
        st.dataframe(df_all.head(10))


        # 导出完整的比较结果
        def to_excel(df):
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine='openpyxl')
            df.to_excel(writer, index=False, sheet_name='比较结果')
            writer.close()
            processed_data = output.getvalue()
            return processed_data


        excel_data = to_excel(df_all)

        # 提供下载按钮导出数据
        st.download_button(
            label="下载完整的比较结果 Excel 文件",
            data=excel_data,
            file_name='比较结果.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
