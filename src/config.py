# 爬取网站所需的配置信息
webInfo = {
    "tokenURL": "http://172.18.100.216/api/blade-auth/ext/api/api/oauth/token",

    "apiUrl": "http://172.18.100.216/api/datacenter/dataapiCfg/dc/getDataByConfigApi",

    "headers": {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.289 Safari/537.36',
        'Connection': 'keep-alive',
        'Authorization': 'Basic c2FiZXI6c2FiZXJfc2VjcmV0',
        'Content-Type': 'application/json;charset=UTF-8',
        'Blade-Auth': None
    },

    "requestPayload": {
        'tenantId': '999999',
        'clientId': '65ABFC56CA9C7FAFDF7A2E599F6C392B',
        'clientSecret': '942846F01B9657F257D1843FD303706A',
        'grantType': 'api'
    },

    "apiData": {
        'cfgName': '数字航道TO武汉局主中心设备详细信息'
    }
}

# 数据库配置信息
dbConfig = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': '数字航道质量评估结果',
    'port': 3306
} 