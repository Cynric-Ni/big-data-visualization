import login_fetch_data
from config import webInfo
import json
from datetime import datetime, timedelta
import pymysql

class DataAnalyzer:
    """数据分析器主类，负责处理数据分析和数据库操作"""
    
    def __init__(self):
        """初始化数据分析器，设置数据库配置"""
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '123456',
            'database': '数字航道质量评估结果',
            'port': 3306
        }
        self.connection = None
        self.cursor = None

    def __enter__(self):
        """上下文管理器入口，建立数据库连接"""
        self.connection = pymysql.connect(**self.db_config)
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口，关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            if exc_type is None:
                self.connection.commit()
            else:
                self.connection.rollback()
            self.connection.close()

    def process_and_save_to_db(self, filtered_data_by_area):
        """
        主要的数据库处理函数，负责处理外业和内业分析数据
        Args:
            filtered_data_by_area: 按区域筛选的数据字典
        """
        try:
            with self:
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.handle_wy_analysis(filtered_data_by_area, current_time)
                self.handle_ny_analysis(filtered_data_by_area, current_time)
        except Exception as e:
            print(f"数据库操作错误: {str(e)}")

    def handle_wy_analysis(self, filtered_data_by_area, current_time):
        """处理外业分析数据"""
        self._setup_table('wy_analysis')
        return self._process_wy_data(filtered_data_by_area, current_time)

    def handle_ny_analysis(self, filtered_data_by_area, current_time):
        """处理内业分析数据"""
        self._setup_table('ny_analysis')
        return self._process_ny_data(filtered_data_by_area, current_time)

    def _setup_table(self, table_name):
        """创建或重建数据表"""
        self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            area VARCHAR(50),
            excellent_count INT,
            good_count INT,
            average_count INT,
            poor_count INT,
            updated_at DATETIME
        )
        """
        self.cursor.execute(create_table_sql)

    def _process_wy_data(self, filtered_data_by_area, current_time):
        """处理外业数据"""
        data = {'excellent': [], 'good': [], 'average': [], 'poor': []}
        for area, rows in filtered_data_by_area.items():
            counts = self._count_wy_analysis(rows)
            self._insert_analysis_data('wy_analysis', area, counts, current_time)
            for key in data:
                data[key].append(counts[key])
        return data

    def _process_ny_data(self, filtered_data_by_area, current_time):
        """处理内业数据"""
        data = {'excellent': [], 'good': [], 'average': [], 'poor': []}
        for area, rows in filtered_data_by_area.items():
            counts = self._count_ny_analysis(rows)
            self._insert_analysis_data('ny_analysis', area, counts, current_time)
            for key in data:
                data[key].append(counts[key])
        return data

    @staticmethod
    def _count_wy_analysis(rows):
        """统计外业分析数据"""
        counts = {'excellent': 0, 'good': 0, 'average': 0, 'poor': 0}
        for row in rows:
            wy_analysis = row.get("WY-analysis")
            if wy_analysis:
                if wy_analysis >= 8:
                    counts['excellent'] += 1
                elif wy_analysis >= 4:
                    counts['good'] += 1
                elif wy_analysis >= 2:
                    counts['average'] += 1
                else:
                    counts['poor'] += 1
        return counts

    @staticmethod
    def _count_ny_analysis(rows):
        """统计内业分析数据"""
        counts = {'excellent': 0, 'good': 0, 'average': 0, 'poor': 0}
        for row in rows:
            ny_analysis = row.get("NY-analysis")
            if ny_analysis:
                if ny_analysis >= 4:
                    counts['excellent'] += 1
                elif ny_analysis >= 2.6:
                    counts['good'] += 1
                elif ny_analysis >= 1.6:
                    counts['average'] += 1
                else:
                    counts['poor'] += 1
        return counts

    def _insert_analysis_data(self, table, area, counts, current_time):
        """插入分析数据到数据库"""
        sql = f"""
        INSERT INTO {table} (area, excellent_count, good_count, average_count, poor_count, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(sql, (area, counts['excellent'], counts['good'],
                                counts['average'], counts['poor'], current_time))

    def get_analysis_data(self):
        """获取分析数据"""
        try:
            with self:
                wy_data = self._fetch_analysis_data('wy_analysis')
                ny_data = self._fetch_analysis_data('ny_analysis')
                return [wy_data, ny_data]
        except Exception as e:
            print(f"获取分析数据错误: {str(e)}")
            return None

    def _fetch_analysis_data(self, table_name):
        """从指定表获取分析数据"""
        sql = f"SELECT excellent_count, good_count, average_count, poor_count FROM {table_name}"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        return [[row[i] for row in results] for i in range(4)]
def main():
    try:
        # 创建API客户端
        client = login_fetch_data.APIClient(webInfo)

        # 获取并保存测绘基本信息及成果资料
        survey_data = client.get_data("数字航道武汉测绘基本信息及成果资料to武汉局")
        workload_data = client.get_data("数字航道武汉测绘工作量数据to武汉局")
        
        # 保���原始数据
        client.save_to_json(workload_data, "测绘工作量")
        client.save_to_json(survey_data, "测绘基本信息")

        # 数据筛选和处理
        try:
            data_list = survey_data.get('data', [])
        except json.JSONDecodeError as e:
            print("JSON 解析错误:", e)
            data_list = []

        # 初步数据筛选
        filtered_data = []
        for row in data_list:
            if isinstance(row, dict) and row.get('XDDW_ID') == '0105' and row.get('CGTJSJ') is not None:
                filtered_data.append(row)

        # 按区域分类数据
        classified_data = {'010512': [], '010513': [], '010514': [], '010511': [], '010515': [],
                          '010517': [], '010516': [], '010518': [], '01051107': [], '01051607': []}

        for row in filtered_data:
            ZXDW_ID = row.get('ZXDW_ID')
            if ZXDW_ID in classified_data:
                classified_data[ZXDW_ID].append(row)

        # 数据匹配和处理
        try:
            workload_list = workload_data.get('data', [])
        except json.JSONDecodeError as e:
            print("JSON 解析错误:", e)
            workload_list = []

        # 数据匹配统计
        match_statistics = {'total_matches': 0, 'areas': {}}
        for area_id, area_rows in classified_data.items():
            match_statistics['areas'][area_id] = 0
            for row in area_rows:
                row_id = row.get('ID')
                match_count = 0
                hsmj_values = []
                
                for b_row in workload_list:
                    if b_row.get('CHRW_ID') == row_id:
                        match_count += 1
                        hsmj_value = b_row.get('HSMJ')
                        if hsmj_value is not None:
                            hsmj_values.append(hsmj_value)
                
                row['RWZJ'] = match_count
                match_statistics['total_matches'] += match_count
                match_statistics['areas'][area_id] += match_count

                if hsmj_values:
                    if 'HSMJ' in row:
                        row['HSMJ'].extend(hsmj_values)
                    else:
                        row['HSMJ'] = hsmj_values

        # 日期转换和计算
        for area_rows in classified_data.values():
            for row in area_rows:
                date_fields = ["CJSJ", "GXSJ", "KGRQ", "CGTJRQ", "XDSJ", "CGTJSJ", "CGWYKS", "CGWYJS"]
                for field in date_fields:
                    if field in row and row[field] is not None:
                        row[field] = datetime.strptime(row[field][:10], "%Y-%m-%d").date()

                if "HSMJ" in row and row.get("HSMJ") is not None:
                    hsmj_values = row["HSMJ"]
                    if isinstance(hsmj_values, list):
                        hsmj_float_values = [float(value) for value in hsmj_values]
                        row["HSMJ"] = hsmj_float_values
                    else:
                        row["HSMJ"] = float(hsmj_values)

        # 最终数据过滤
        filtered_data_by_area = {'010512': [], '010513': [], '010514': [], '010511': [], '010515': [],
                                '010517': [], '010516': [], '010518': [], '01051107': [], '01051607': []}

        for area_rows in classified_data.values():
            for row in area_rows:
                if "XDSJ" in row and row["XDSJ"] is not None and row["XDSJ"].year >= 2024:
                    area = row["SSJG_ID"]
                    if area in filtered_data_by_area:
                        filtered_data_by_area[area].append(row)

        # 在计算最终指标的循环中添加最大值跟踪
        max_wy_analysis = float('-inf')
        max_info = None

        # 计算最终指标
        for area, rows in filtered_data_by_area.items():
            for row in rows:
                hsmj_values = row.get('HSMJ')
                if hsmj_values:
                    if isinstance(hsmj_values, list):
                        hsmj_sum = sum(hsmj_values)
                        row["HSMJZJ"] = max(hsmj_sum, 8)
                    else:
                        row["HSMJZJ"] = max(float(hsmj_values), 8)

                if all(key in row and row[key] is not None for key in ["CGWYKS", "CGWYJS", "CGTJSJ"]):
                    row["WY-DAYS"] = (row["CGWYJS"] - row["CGWYKS"]).days + 1
                    row["NY-DAYS"] = (row["CGTJSJ"] - row["CGWYJS"]).days + 1
                    
                    if "HSMJZJ" in row:
                        row["WY-analysis"] = row["HSMJZJ"] / row["WY-DAYS"]
                        row["NY-analysis"] = row["HSMJZJ"] / row["NY-DAYS"]
                        
                        # 在这里添加最大值比较
                        if row["WY-analysis"] > max_wy_analysis:
                            max_wy_analysis = row["WY-analysis"]
                            max_info = {
                                '区域': area,
                                'WY-analysis值': row["WY-analysis"],
                                '任务名称': row.get('RWMC'),
                                '测绘地点': row.get('CHDD'),
                                '外业开始时间': row.get('CGWYKS'),
                                '外业结束时间': row.get('CGWYJS')
                            }

        # 保存处理后的数据
        try:
            with open('filtered_data_by_area.json', 'w', encoding='utf-8') as f:
                json.dump(filtered_data_by_area, f, ensure_ascii=False, indent=2, default=str)
            print("数据已成功保存到 filtered_data_by_area.json")
        except Exception as e:
            print(f"保存JSON文件时出错: {str(e)}")

        # 数据库操作
        print("\n=== 开始数据库操作 ===")
        analyzer = DataAnalyzer()
        analyzer.process_and_save_to_db(filtered_data_by_area)
        print("数据已成功保存到数据库")

        # 打印最大值信息
        print("\n=== 最大外业分析值信息 ===")
        if max_info:
            for key, value in max_info.items():
                print(f"{key}: {value}")
        else:
            print("未找到有效的外业分析值")

        # 获取分析数据
        print("\n=== 获取分析数据 ===")
        analysis_results = analyzer.get_analysis_data()
        
        # 打印分析结果
        if analysis_results:
            print("\n=== 分析结果 ===")
            print("外业分析数据:", analysis_results[0])
            print("内业分析数据:", analysis_results[1])

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()