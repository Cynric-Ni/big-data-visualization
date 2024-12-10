import requests
import json

login_url = 'http://172.18.100.216/api/blade-auth/ext/api/api/oauth/token/'
url = 'http://172.18.100.216/api/datacenter/dataapiCfg/dc/getDataByConfigApi'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.289 Safari/537.36',
    'Connection': 'keep-alive',
    'Authorization': 'Basic c2FiZXI6c2FiZXJfc2VjcmV0',
    'Content-Type': 'application/json;charset=UTF-8'
}

base_info_data = {
    'tenantId': '999999',
    'clientId': '65ABFC56CA9C7FAFDF7A2E599F6C392B',
    'clientSecret': '942846F01B9657F257D1843FD303706A',
    'grantType': 'api'
}

base_workload_data = {
    'tenantId': '999999',
    'clientId': '65ABFC56CA9C7FAFDF7A2E599F6C392B',
    'clientSecret': '942846F01B9657F257D1843FD303706A',
    'grantType': 'api'
}

api_base_data = {
    'cfgName': '数字航道TO武汉局主中心设备详细信息'
}

api_workload_data = {
    'cfgName': '数字航道TO武汉局主中心设备使用信息'
}


def api_res(login_url, url, headers, api_data, base_data):  ##可以添加file_str参数
    res = requests.post(login_url, headers=headers, json=base_data)
    # @test
    # print(res.text)
    result = json.loads(res.text)
    access_token = result['data']['access_token']
    # @test
    # print(access_token)
    headers["Blade-Auth"] = access_token
    res_api = requests.post(url, headers=headers, json=api_data)
    rep = res_api.json()
    # @test
    # print(type(rep))
    headers["Blade-Auth"] = ''
    return rep


rep1 = api_res(login_url=login_url, url=url, headers=headers, base_data=base_info_data, api_data=api_base_data)

filename = 'rep_data.json'

# 将rep写入到文件中
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(rep1, f, ensure_ascii=False, indent=4)

print(f"JSON数据已保存到文件 {filename}")

rep2 = api_res(login_url=login_url, url=url, headers=headers, base_data=base_workload_data,
               api_data=api_workload_data)
filename = 'rep_data2.json'

# 将rep2写入到文件中
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(rep2, f, ensure_ascii=False, indent=4)

print(f"JSON数据已保存到文件 {filename}")
