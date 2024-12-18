# 数据处理流程说明

## 项目结构
project/
├── main.py # 主程序入口
├── src/
│ ├── NW.py # 数据处理核心脚本
│ ├── login_fetch_data.py # API客户端
│ ├── config.py # 配置文件
│ └── maintest.py # 测试脚本
├── credentials.json # API凭证配置
├── pyproject.toml # 项目配置文件
└── .gitignore # Git忽略文件

## 功能概述
该项目主要用于获取和处理测绘相关数据，包括测绘基本信息和工作量数据的获取、匹配和分析。

## 数据处理流程

### 1. 数据获取
- 通过API获取两类数据：
  - 测绘基本信息 (`survey_data`)
  - 工作量数据 (`workload_data`)
- 数据获取后自动保存为带时间戳的JSON文件

### 2. 数据筛选
- 对测绘基本信息进行初步筛选：
  - 筛选条件：`XDDW_ID='0105'` 且 `CGTJSJ` 不为空
- 按区域分类：
  - 根据 `ZXDW_ID` 将数据分类到不同区域
  - 支持的区域代码：010512, 010513, 010514, 010511, 010515等

### 3. 数据匹配与处理
- 数据匹配：
  - 将工作量数据与筛选后的记录进行匹配
  - 匹配依据：`ID` 和 `CHRW_ID`
- 计算指标：
  - `RWZJ`：任务计数
  - `HSMJ`：汇总面积值

### 4. 数据转换
- 日期处理：
  - 将日期字符串转换为日期对象
  - 处理字段：CJSJ, GXSJ, KGRQ, CGTJRQ等
- 数值处理：
  - 将面积值转换为浮点数

### 5. 指标计算
- 筛选2024年及以后的数据
- 计算关键指标：
  - `HSMJZJ`：面积总计（最小值为8）
  - `WY-DAYS`：外业天数（CGWYJS - CGWYKS + 1）
  - `NY-DAYS`：内业天数（CGTJSJ - CGWYJS + 1）
  - `WY-analysis`：外业分析（HSMJZJ / WY-DAYS）
  - `NY-analysis`：内业分析（HSMJZJ / NY-DAYS）

## 配置说明
- `config.py`：包含API接口配置
- `credentials.json`：存储API访问凭证
- 确保配置文件包含正确的API访问信息和凭证

## 使用说明
1. 确保配置文件正确设置
2. 运行 main.py 脚本
3. 检查生成的JSON文件和计算结果

## 注意事项
- 需要正确配置API访问凭证
- 确保网络连接正常
- 数据处理过程中会自动进行数据类型转换