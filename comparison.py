import streamlit as st
import pandas as pd
from io import BytesIO
import uuid

st.title("增长汪汪 - 面向产研团队的 BI 数据分析工具")

st.header("数据比较")

st.subheader("上传 Excel 数据源")

file1 = st.file_uploader("上传第一个文件", type=["xlsx", "xls"])
file2 = st.file_uploader("上传第二个文件", type=["xlsx", "xls"])

def compare_with_same_headers(df1, df2):
    st.success("检测到表头一致，正在进行比较。")
    proceed_to_compare = True
    if proceed_to_compare:
        mapped_columns = df1.columns.tolist()
        df_all = highlight_differences(df1, df2, mapped_columns)
        display_and_download_results(df_all)

def compare_with_different_headers(df1, df2):
    st.warning("表头不一致，请进行列映射。")
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
                st.rerun()  # 使用 st.rerun()
        # 更新映射关系
        mapping['col1'] = col1
        mapping['col2'] = col2

    # 应用映射关系
    if st.button('完成映射'):
        if st.session_state.mappings:
            df2_mapped = apply_mappings(df2, st.session_state.mappings)
            # 获取映射后的列名列表
            mapped_columns = [mapping['col1'] for mapping in st.session_state.mappings]
            df_all = highlight_differences(df1, df2_mapped, mapped_columns)
            display_and_download_results(df_all)
        else:
            st.warning("请至少添加一个列的对应关系。")
            st.stop()
    else:
        st.info("添加列的对应关系并点击“完成映射”按钮来进行数据比较。")
        st.stop()  # 等待用户完成映射后再继续

def apply_mappings(df2, mappings):
    # 将 df2 的列名按照映射关系重命名为 df1 的列名
    mapping_dict = {mapping['col2']: mapping['col1'] for mapping in mappings}
    df2_mapped = df2.rename(columns=mapping_dict)
    # 只保留映射后的列
    df2_mapped = df2_mapped[list(mapping_dict.values())]
    return df2_mapped

def highlight_differences(df1, df2_mapped, mapped_columns):
    # df1: 原始的 df1 数据框，包含所有列
    # df2_mapped: 根据映射关系重命名后的 df2 数据框，只包含映射后的列
    # mapped_columns: 映射后的列名列表（来自 df1）

    # 重置索引以确保正确对齐
    df1.reset_index(drop=True, inplace=True)
    df2_mapped.reset_index(drop=True, inplace=True)

    # 创建一个新的 DataFrame，包含 df1 的所有数据
    df_all = df1.copy()

    # 创建一个空的 DataFrame，用于存储差异标记
    df_all_diff = pd.DataFrame('', index=df1.index, columns=mapped_columns)

    # 比较映射的列，创建差异标记
    comparison_values = df1[mapped_columns].values == df2_mapped[mapped_columns].values
    rows, cols = df1[mapped_columns].shape
    for i in range(rows):
        for j in range(cols):
            if not comparison_values[i, j]:
                col_name = mapped_columns[j]
                df_all_diff.at[i, col_name] = f"{df1.at[i, col_name]} --> {df2_mapped.at[i, col_name]}"

    # 将差异结果添加到 df_all 中
    for column in mapped_columns:
        df_all[f"{column}_差异"] = df_all_diff[column]

    # 添加一个列，标记每一行是否有差异
    df_all['是否有差异'] = df_all_diff.apply(lambda x: '有差异' if any(x != '') else '无差异', axis=1)

    return df_all

def highlight_diff_cells(data, diff_columns):
    def apply_highlight(val):
        return 'background-color: yellow' if val != '' else ''
    return data.style.applymap(apply_highlight, subset=diff_columns)

def display_and_download_results(df_all):
    # 添加筛选控件
    show_differences_only = st.checkbox("仅显示有差异的行", value=False)

    if show_differences_only:
        df_display = df_all[df_all['是否有差异'] == '有差异']
    else:
        df_display = df_all

    # 显示前10行结果
    st.write("比较结果（前 10 行）：")
    df_display_head = df_display.head(10)

    # 直接显示数据，不应用高亮样式
    st.dataframe(df_display_head)

    # 导出完整的比较结果
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='比较结果')
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

if file1 and file2:
    # 读取文件
    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)

    # 检测表头是否一致
    if df1.columns.tolist() == df2.columns.tolist():
        compare_with_same_headers(df1, df2)
    else:
        compare_with_different_headers(df1, df2)
else:
    st.info("请上传两个 Excel 文件以进行比较。")
