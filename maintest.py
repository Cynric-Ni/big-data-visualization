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

    def save_to_json(self, data, filename):
        """
        保存数据到JSON文件
        :param data: 要保存的数据
        :param filename: 文件名（不需要.json后缀）
        """
        try:
            # 确保文件名以.json结尾
            if not filename.endswith('.json'):
                filename = f"{filename}.json"

            # 添加时间戳到文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename.rsplit('.', 1)[0]}_{timestamp}.json"

            # 保存数据
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logging.info(f"数据已保存到文件: {filename}")
            return filename
        except Exception as e:
            logging.error(f"保存JSON文件时出错: {str(e)}")
            raise

# 使用示例
if __name__ == "__main__":
    try:
        client = APIClient(webInfo)

        # 获取并保存设备详细信息
        device_details = client.get_device_details()
        client.save_to_json(device_details, "device_details")

        # 获取并保存设备使用信息
        device_usage = client.get_device_usage()
        client.save_to_json(device_usage, "device_usage")

        # 获取并保存设备领用记录
        device_records = client.get_device_records()
        client.save_to_json(device_records, "device_records")

        # 获取并保存航道保护工作信息
        channel_protection = client.get_channel_protection()
        client.save_to_json(channel_protection, "channel_protection")

    except Exception as e:
        logging.error(f"程序执行错误: {str(e)}")