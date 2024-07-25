import pandas as pd
import streamlit as st
import io
import json


# 定义函数，用于提取销售记录
def extract_sales_records(json_data):
    # 解析JSON数据
    data = json.loads(json_data)

    # 提取销售记录
    sales_records = data.get('result', [])

    # 将销售记录转换为DataFrame
    df = pd.DataFrame(sales_records)

    # 选择需要的列
    df = df[['date', 'prodSkuId', 'salesNumber']]

    return df

#显示页面标题
st.title('出海销售订单数据提取工具')

# 提供一个多行文本框，用于输入JSON数据
json_data = st.text_area('请输入JSON数据', height=300, help='请粘贴销售订单数据的JSON格式数据')

# 增加一个勾选框，选择是否剔除salesNumber为0的记录
remove_zero_sales = st.checkbox('剔除销售数量为0的记录', value=True)

# 设置为两列，比例为 3:1
col1, col2 = st.columns([3, 1])

with col1:
    # 添加一个按钮，用于触发数据提取操作
    if st.button('提取销售记录',use_container_width=True, type='primary'):

        #验证输入的内容是否符合JSON格式
        try:
            json.loads(json_data)
        except json.JSONDecodeError:
            st.error('输入的数据不符合JSON格式，请重新输入')
            st.stop()

        # 调用函数，提取销售记录
        df = extract_sales_records(json_data)

        # 按 date 列从早到晚排序
        df = df.sort_values('date')

        # prodSkuld列转换为字符串
        df['prodSkuId'] = df['prodSkuId'].astype(str)

        # 如果勾选了剔除销售数量为0的记录，则执行下面的代码
        if remove_zero_sales:
            df = df[df['salesNumber'] > 0]

        # 对列更名
        df.columns = ['日期', 'SKU ID', '销量']

with col2:
    # 添加一个按钮，用于下载提取的数据，格式为xlsx
    if 'df' in locals():
        to_excel = io.BytesIO()
        with pd.ExcelWriter(to_excel, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        to_excel.seek(0)
        st.download_button(
            label='下载数据',
            use_container_width=True,
            data=to_excel,
            file_name='sales_records.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

# 如果 df 存在，则显示提取的数据
if 'df' in locals():
    # 显示提取的数据
    st.dataframe(df, use_container_width=True)
