import logging
import time
import requests
import json
from datetime import datetime
from config import webInfo  # 导入配置
import os

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
        self.tokens = {}
        self.token_timestamps = {}
        
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        credentials_path = os.path.join(current_dir, '..', 'credentials.json')
        
        # 加载凭证配置
        try:
            with open(credentials_path, 'r', encoding='utf-8') as f:
                self.api_credentials = json.load(f)
        except FileNotFoundError:
            logging.error(f"找不到凭证配置文件: {credentials_path}")
            raise

    def _get_token(self, cfg_name):
        """获取新token"""
        if cfg_name not in self.api_credentials:
            raise ValueError(f"未找到配置名称 '{cfg_name}' 的凭证信息")

        try:
            payload = self.webinfo["requestPayload"].copy()
            payload.update(self.api_credentials[cfg_name])
            
            logging.info(f"Getting token for cfg_name: {cfg_name}")
            response = requests.post(
                self.webinfo["tokenURL"],
                headers=self.webinfo["headers"],
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                return result['data']['access_token']
            raise Exception(f"Token获取失败: {result.get('msg')}")
        except Exception as e:
            logging.error(f"Token获取错误: {str(e)}")
            raise

    def get_data(self, cfg_name):
        """
        通用数据获取方法
        :param cfg_name: 配置名称，必须与credentials.json中的键名完全匹配
        :return: 获取的数据
        """
        if cfg_name not in self.api_credentials:
            raise ValueError(f"���找到配置名称 '{cfg_name}' 的凭证信息")

        return self.fetch_data(cfg_name)

    def get_valid_token(self, cfg_name=None):
        """获取有效的token"""
        current_time = time.time()
        
        # 使用cfg_name作为key，如果为None则使用'default'
        token_key = cfg_name or 'default'
        
        # 检查是否需要刷新token
        if (token_key not in self.tokens or 
            token_key not in self.token_timestamps or
            current_time - self.token_timestamps[token_key] > 3600):  # token 1小时后刷新
            
            self.tokens[token_key] = self._get_token(cfg_name)
            self.token_timestamps[token_key] = current_time
        
        return self.tokens[token_key]

    def fetch_data(self, cfg_name):
        """获取数据的通用方法"""
        cache_key = f"data_{cfg_name}"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return cached_data

        try:
            token = self.get_valid_token(cfg_name)
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
        
        # 直接使用credentials.json中的键名作为配置名称
        for cfg_name in client.api_credentials.keys():
            try:
                data = client.get_data(cfg_name)
                # 生成简化的文件名
                filename = cfg_name.split("to")[0].strip().replace("数字航道", "").replace("武汉局主中心", "")
                client.save_to_json(data, filename)
            except Exception as e:
                logging.error(f"获取数据失败 ({cfg_name}): {str(e)}")

    except Exception as e:
        logging.error(f"程序执行错误: {str(e)}")