# 增长汪汪 - 面向产品运营团队的 BI 数据分析工具
## 项目要求
- Python 3.10+
- Azure ChatGPT：如果需要对数据源进行异常值检测，需要配置 Azure ChatGPT 的环境变量

## 本地开发
1. 安装 [pipenv](https://pipenv.pypa.io/en/latest/)：`brew install pipenv`
2. 在项目根目录下运行 `pipenv install` 安装开发环境以及依赖
3. 运行 `pipenv shell` 进入虚拟环境
4. 创建 `.env` 文件把 `env.example` 文件中的内容复制到 `.env` 文件中，并填写相应的配置
5. 运行 `streamlit run xxx.py` 启动服务，`xxx.py` 为你要启动的文件

## 产品功能点
1. `comparison.py`：比较两份 Excel 数据源的差异
   1. 当数据源表头一致时候，可以直接比较两份数据源的差异
   2. 当数据源表头不一致的时候，可以通过配置表头映射关系，比较两份数据源的差异
2. `anomaly.py`：检测数据源中的异常值
   1. 可以通过配置异常值检测规则，检测数据源中的异常值


## 使用说明
演示教程[视频链接](https://caqw5i9s19z.feishu.cn/wiki/X7B8w3ogSiN58ikGbwcchz8LnTc?from=from_copylink)
### 异常值检测
1. 上传 Excel 文件
2. 选择需要检测的列
3. 针对每一列输入异常值检测规则
4. 点击 `开始检测` 按钮，等待检测结果
5. 点击 `下载结果` 按钮，下载包含检测结果的 Excel 文件