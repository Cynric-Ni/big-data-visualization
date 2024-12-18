import login_fetch_data
from config import webInfo
import json
from datetime import datetime, timedelta

try:
    client = login_fetch_data.APIClient(webInfo)

    # 获取并保存测绘基本信息及成果资料
    survey_data = client.get_data("数字航道武汉测绘基本信息及成果资料to武汉局")
    
    # 获取并保存武汉测绘工作量数据
    workload_data = client.get_data("数字航道武汉测绘工作量数据to武汉局")
    
    print("Survey Data:", json.dumps(survey_data, indent=2)[:500])  # 只打印前500个字符
    print("Workload Data:", json.dumps(workload_data, indent=2)[:500])
    
    client.save_to_json(workload_data, "测绘工作量")
    client.save_to_json(survey_data, "测绘基本信息")

    # # 测试验证1：检查数据获取是否成功
    # print("=== 数据获取验证 ===")
    # print(f"survey_data 记录数: {len(survey_data.get('data', []))}")
    # print(f"workload_data 记录数: {len(workload_data.get('data', []))}")

    try:
        data_list = survey_data.get('data', [])
    except json.JSONDecodeError as e:
        print("JSON 解析错误:", e)
        data_list = []

    filtered_data = []
    for row in data_list:
        if isinstance(row, dict) and row.get('XDDW_ID') == '0105' and row.get('CGTJSJ') is not None:
            filtered_data.append(row)

    # # 测试验证2：检查数据筛选结果
    # print("\n=== 数据筛选验证 ===")
    # print(f"筛选后的记录数: {len(filtered_data)}")
    # print(f"第一条记录示例: {filtered_data[0] if filtered_data else 'No data'}")

    classified_data = {'010512': [], '010513': [], '010514': [], '010511': [], '010515': [],
                      '010517': [], '010516': [], '010518': [], '01051107': [], '01051607': []}

    for row in filtered_data:
        ZXDW_ID = row.get('ZXDW_ID')
        if ZXDW_ID in classified_data:
            classified_data[ZXDW_ID].append(row)

    # # 测试验证3：检查分类结果
    # print("\n=== 数据分类验证 ===")
    # for area, data in classified_data.items():
    #     print(f"区域 {area} 的记录数: {len(data)}")

    try:
        data_list = workload_data.get('data', [])
    except json.JSONDecodeError as e:
        print("JSON 解析错误:", e)
        data_list = []

    # 数据匹配和处理
    match_statistics = {'total_matches': 0, 'areas': {}}
    
    for area_id, area_rows in classified_data.items():
        match_statistics['areas'][area_id] = 0
        for row in area_rows:
            row_id = row.get('ID')
            match_count = 0
            hsmj_values = []
            
            for b_row in data_list:
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

    # # 测试验证4：检查匹配统计
    # print("\n=== 匹配统计验证 ===")
    # print(f"总匹配数: {match_statistics['total_matches']}")
    # for area_id, matches in match_statistics['areas'].items():
    #     print(f"区域 {area_id} 匹配数: {matches}")

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

    # # 测试验证5：检查日期转换
    # print("\n=== 日期转换验证 ===")
    # sample_row = next((row for rows in classified_data.values() for row in rows), None)
    # if sample_row:
    #     print("样本数据日期段类型:")
    #     for field in date_fields:
    #         if field in sample_row:
    #             print(f"{field}: {type(sample_row[field])}")

    # 最终数据过滤和计算
    filtered_data_by_area = {'010512': [], '010513': [], '010514': [], '010511': [], '010515': [],
                            '010517': [], '010516': [], '010518': [], '01051107': [], '01051607': []}

    for area_rows in classified_data.values():
        for row in area_rows:
            if "XDSJ" in row and row["XDSJ"] is not None and row["XDSJ"].year >= 2024:
                area = row["SSJG_ID"]
                if area in filtered_data_by_area:
                    filtered_data_by_area[area].append(row)

    # 计算最终指标
    calculation_statistics = {'total_records': 0, 'processed_records': 0}
    
    for area, rows in filtered_data_by_area.items():
        calculation_statistics['total_records'] += len(rows)
        for row in rows:
            try:
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
                        calculation_statistics['processed_records'] += 1
                    else:
                        print(f"处理失败 - 缺少HSMJZJ字段:", json.dumps(row, ensure_ascii=False, default=str))
                else:
                    print(f"处理失败 - 缺少必要日期字段:", json.dumps(row, ensure_ascii=False, default=str))
            except Exception as e:
                print(f"处理失败 - 计算错误: {str(e)}")
                print(f"问题数据:", json.dumps(row, ensure_ascii=False, default=str))

    # Save filtered_data_by_area to JSON
    # try:
    #     with open('filtered_data_by_area.json', 'w', encoding='utf-8') as f:
    #         json.dump(filtered_data_by_area, f, ensure_ascii=False, indent=2, default=str)
    #     print("数据已成功保存到 filtered_data_by_area.json")
    # except Exception as e:
    #     print(f"保存JSON文件时出错: {str(e)}")

    # 测试验证6：最终计算验证
    # print("\n=== 最终计算验证 ===")
    # print(f"总记录数: {calculation_statistics['total_records']}")
    # print(f"成功处理记录数: {calculation_statistics['processed_records']}")
    # success_rate = (calculation_statistics['processed_records'] / calculation_statistics['total_records'] * 100 
    #                if calculation_statistics['total_records'] > 0 else 0)
    # print(f"处理成功率: {success_rate:.2f}%")

except Exception as e:
    print(f"Error: {str(e)}")
