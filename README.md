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

## 核心函数说明

### 数据库操作函数

#### 主要处理函数
- `process_and_save_to_db(filtered_data_by_area)`: 主要的数据库处理函数，负责连接数据库并处理外业和内业分析数据
- `handle_wy_analysis(cursor, filtered_data_by_area, current_time)`: 处理外业分析数据，包括创建表和插入数据
- `handle_ny_analysis(cursor, filtered_data_by_area, current_time)`: 处理内业分析数据，包括创建表和插入数据

#### 数据表操作
- `setup_table(cursor, table_name)`: 创建或重建数据表（'wy_analysis' 或 'ny_analysis'）

#### 数据处理函数
- `process_wy_data(cursor, filtered_data_by_area, current_time)`: 处理外业数据并��结果插入数据库
- `process_ny_data(cursor, filtered_data_by_area, current_time)`: 处理内业数据并将结果插入数据库

#### 数据统计函数
- `count_wy_analysis(rows)`: 统计外业分析数据的各等级数量
  - 评分标准：
    - ≥ 8: 优秀
    - ≥ 4: 良好
    - ≥ 2: 一般
    - < 2: 差
- `count_ny_analysis(rows)`: 统计内业分析数据的各等级数量
  - 评分标准：
    - ≥ 4: 优秀
    - ≥ 2.6: 良好
    - ≥ 1.6: 一般
    - < 1.6: 差

#### 数据库访问函数
- `insert_analysis_data(cursor, table, area, counts, current_time)`: 将分析结果插入数据库
- `get_analysis_data()`: 从数据库获取分析结果
- `fetch_analysis_data(cursor, table_name)`: 从指定表中获取分析数据

### 处理流程
1. 通过 `process_and_save_to_db` 连接数据库并启动处理流程
2. 分别通过 `handle_wy_analysis` 和 `handle_ny_analysis` 处理外业和内业数据
3. 使用 `setup_table` 创建必要的数据表
4. 通过 `process_wy_data` 和 `process_ny_data` 处理具体数据
5. 使用 `count_wy_analysis` 和 `count_ny_analysis` 进行数据统计
6. 通过 `insert_analysis_data` 将结果存入数据库
7. 可以通过 `get_analysis_data` 和 `fetch_analysis_data` 获取分析结果

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

## 代码重构分析

### 类封装建议

#### 优点：
1. **状态管理更清晰**
   - 数据库配置可以作为类的属性
   - 数据库连接可以更好地管理生命周期
   - 可以避免重复创建数据库连接

2. **更好的组织结构**
   - 相关的函数可以更好地组织在一起
   - 可以将外业和内业分析分成不同的子类
   - 更容易实现依赖注入

3. **更容易扩展**
   - 可以通过继承来添加新的分析方法
   - 更容易添加新的数据处理策略
   - 更容易实现接口模式

4. **更好的封装性**
   - 可以控制内部实现的访问
   - 提供更清晰的公共接口
   - 更好的数据隐藏

#### 可能的类结构：
```python
class DataAnalyzer:
    def __init__(self, db_config):
        self.db_config = db_config
        self.connection = None

class FieldworkAnalyzer(DataAnalyzer):
    # 处理外业相关的分析

class OfficeWorkAnalyzer(DataAnalyzer):
    # 处理内业相关的分析

class DatabaseManager:
    # 处理数据库连接和基本操作
```

### 重构建议
考虑到当前代码的功能和复杂度，建议采用一个中等程度的封装：

1. 创建一个主要的 `DataAnalyzer` 类，包含：
   - 数据库配置和连接管理
   - 数据处理方法
   - 分析功能

2. 保持现有的函数结构，但将它们组织在类中
3. 使用类属性存储配置信息
4. 提供清晰的公共接口

这样可以在获得面向对象编程好处的同时，避免过度设计。

#### 潜在的问题：
1. **可能过度设计**
   - 当前的功能可能不需要这么复杂的结构
   - 可能增加代码的复杂性

2. **性能考虑**
   - 类的实例化可能带来额外开销
   - 需要考虑内存使用



