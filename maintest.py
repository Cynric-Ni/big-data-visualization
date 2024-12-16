import logging
import time
import requests
import json
from datetime import datetime
#爬取网站所需的东西
webInfo = {
    "tokenURL":"http://172.18.100.216/api/blade-auth/ext/api/api/oauth/token",

    "apiUrl":"http://172.18.100.216/api/datacenter/dataapiCfg/dc/getDataByConfigApi",

    "headers":{
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.289 Safari/537.36',
        'Connection': 'keep-alive',
        'Authorization': 'Basic c2FiZXI6c2FiZXJfc2VjcmV0',
        'Content-Type': 'application/json;charset=UTF-8',
        'Blade-Auth': None
    },

    "requestPayload":{
        'tenantId': '999999',
        'clientId': '65ABFC56CA9C7FAFDF7A2E599F6C392B',
        'clientSecret': '942846F01B9657F257D1843FD303706A',
        'grantType': 'api'
    },


    "apiData":{
        'cfgName':'数字航道TO武汉局主中心设备详细信息'
    }

}
# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class DataCache:
    def __init__(self, expire_time=300):  # 5分钟过期
        self.cache = {}
        self.expire_time = expire_time

    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.expire_time:
                return data
        return None

    def set(self, key, data):
        self.cache[key] = (data, time.time())


class APIClient:
    def __init__(self, webinfo):
        self.webinfo = webinfo
        self.cache = DataCache()
        self.token = None
        self.token_timestamp = None

    def _get_token(self):
        """获取新token"""
        try:
            response = requests.post(
                self.webinfo["tokenURL"],
                headers=self.webinfo["headers"],
                json=self.webinfo["requestPayload"]
            )
            response.raise_for_status()
            result = response.json()
            if result.get('success'):
                return result['data']['access_token']
            raise Exception(f"Token获取失败: {result.get('msg')}")
        except Exception as e:
            logging.error(f"Token获取错误: {str(e)}")
            raise

    def get_valid_token(self):
        """获取有效的token"""
        current_time = time.time()
        if not self.token or not self.token_timestamp or \
                current_time - self.token_timestamp > 3600:  # token 1小时后刷新
            self.token = self._get_token()
            self.token_timestamp = current_time
        return self.token

    def fetch_data(self, cfg_name):
        """获取数据的通用方法"""
        cache_key = f"data_{cfg_name}"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return cached_data

        try:
            token = self.get_valid_token()
            headers = self.webinfo["headers"].copy()
            headers['Blade-Auth'] = token

            response = requests.post(
                self.webinfo["apiUrl"],
                headers=headers,
                json={"cfgName": cfg_name}
            )
            response.raise_for_status()
            result = response.json()

            if result.get('success'):
                self.cache.set(cache_key, result['data'])
                return result['data']
            raise Exception(f"数据获取失败: {result.get('msg')}")

        except Exception as e:
            logging.error(f"数据获取错误 ({cfg_name}): {str(e)}")
            raise

    def get_device_details(self):
        """获取设备详细信息"""
        return self.fetch_data("数字航道TO武汉局主中心设备详细信息")

    def get_device_usage(self):
        """获取设备使用信息"""
        return self.fetch_data("数字航道TO武汉局主中心设备使用信息")

    def get_device_records(self):
        """获取设备领用记录"""
        return self.fetch_data("数字航道TO武汉局主中心设备领用记录")

    def get_channel_protection(self):
        """获取航道保护工作信息"""
        return self.fetch_data("数字航道TO武汉局主中心航道保护工作信息")


# 使用示例
if __name__ == "__main__":
    try:
        # 使用您原有的webInfo配置创建客户端
        client = APIClient(webInfo)

        # 获取设备详细信息
        device_details = client.get_device_details()
        print("设备详细信息:", device_details)

        # 获取设备使用信息
        device_usage = client.get_device_usage()
        print("设备使用信息:", device_usage)

    except Exception as e:
        logging.error(f"程序执行错误: {str(e)}")