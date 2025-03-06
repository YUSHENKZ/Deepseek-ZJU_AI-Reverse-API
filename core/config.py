import os
from datetime import datetime
from typing import Dict
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self.model_name = os.getenv('MODEL_NAME', 'deepseek-v3')
        self.api_keys = self._load_api_keys()

    def _load_api_keys(self) -> Dict[str, str]:
        """加载API密钥配置"""
        api_keys = {}
        
        # 遍历所有环境变量
        for key, value in os.environ.items():
            if key.startswith('API_KEY_'):
                if '=' in value:
                    api_key, expire = value.split('=', 1)
                    api_keys[api_key.strip()] = expire.strip()
        
        if not api_keys:
            print("警告: 未能加载到任何API密钥")
            
        return api_keys

    def is_valid_key(self, api_key: str) -> bool:
        """验证API密钥是否有效"""
        # 添加调试输出
        print(f"正在验证密钥: {api_key}")
        print(f"已加载的密钥列表: {list(self.api_keys.keys())}")
        
        if api_key not in self.api_keys:
            print(f"密钥 {api_key} 未找到")
            return False
        
        expire_time = self.api_keys[api_key]
        print(f"密钥 {api_key} 的过期时间: {expire_time}")
        
        # 永久有效
        if expire_time == 'permanent':
            return True
            
        try:
            # 将日期字符串转换为时间戳
            expire_date = datetime.strptime(expire_time, '%Y-%m-%d')
            is_valid = datetime.now() < expire_date
            print(f"密钥验证结果: {'有效' if is_valid else '已过期'}")
            return is_valid
        except ValueError as e:
            print(f"日期格式错误: {e}")
            return False

    def is_valid_model(self, model_name: str) -> bool:
        """验证模型名称是否有效"""
        return model_name == self.model_name 