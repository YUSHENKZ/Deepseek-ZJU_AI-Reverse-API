import json
import uuid
import time
import logging
import requests
import re
from typing import Iterator, Optional

# 配置日志记录器
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class 请求限制器:
    """请求频率限制器"""
    def __init__(self, 最大请求数: int = 20, 时间窗口: int = 60):
        self.最大请求数 = 最大请求数
        self.时间窗口 = 时间窗口
        self.请求记录 = []
    
    def 是否可请求(self) -> bool:
        """检查是否可以发送新请求"""
        当前时间 = time.time()
        self.请求记录 = [req_time for req_time in self.请求记录 
                    if 当前时间 - req_time < self.时间窗口]
        
        if len(self.请求记录) < self.最大请求数:
            self.请求记录.append(当前时间)
            return True
        return False

    def 等待请求(self):
        """如果超出频率限制，等待直到可以请求"""
        while not self.是否可请求():
            time.sleep(1)

class ZJU_AI聊天API:
    """ZJU_AI聊天API核心类"""
    def __init__(self, 调试模式: bool = False):
        self.调试模式 = 调试模式
        if self.调试模式:
            logger.setLevel(logging.DEBUG)
            
        self.base_url = "https://open.zju.edu.cn"
        self.app_key = "cu3m3jodetcjeetbl2f0"
        self.会话 = requests.Session()
        self.csrf令牌 = None
        self.会话ID = None
        self.初始化()

    def 初始化(self):
        """初始化会话"""
        try:
            # 1. 首次访问页面
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Host": "open.zju.edu.cn",
                "Pragma": "no-cache",
                "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            }
            
            初始响应 = self.会话.get(
                f"{self.base_url}/product/llm/chat/{self.app_key}",
                headers=headers
            )
            初始响应.raise_for_status()

            if self.调试模式:
                logger.debug(f"初始响应状态码: {初始响应.status_code}")
                logger.debug(f"初始响应头: {dict(初始响应.headers)}")
                logger.debug(f"初始响应内容长度: {len(初始响应.text)}")

            # 2. 从Set-Cookie中获取CSRF令牌
            cookies = dict(初始响应.cookies)
            self.csrf令牌 = cookies.get('x-csrf-token')
            
            if not self.csrf令牌:
                self.csrf令牌 = self._生成CSRF令牌()
                logger.warning("未找到CSRF令牌，使用生成的令牌")

            if self.调试模式:
                logger.debug(f"使用的CSRF令牌: {self.csrf令牌}")

            # 3. 创建会话
            创建会话响应 = self.会话.post(
                f"{self.base_url}/api/proxy/chat/v2/create_conversation",
                headers=self._获取API请求头(),
                json={
                    "AppKey": self.app_key
                }
            )
            创建会话响应.raise_for_status()
            
            # 4. 从响应中获取会话ID
            会话数据 = 创建会话响应.json()
            if self.调试模式:
                logger.debug(f"创建会话响应: {创建会话响应.text}")
                
            self.会话ID = 会话数据.get("Conversation", {}).get("AppConversationID")
            if not self.会话ID:
                raise Exception("未能获取会话ID")

            if self.调试模式:
                logger.debug("会话初始化成功")
                logger.debug(f"会话ID: {self.会话ID}")

        except Exception as e:
            logger.error(f"初始化失败: {str(e)}")
            if self.调试模式:
                logger.exception("详细错误信息")
            raise

    def _获取API请求头(self) -> dict:
        """获取API请求通用头部"""
        return {
            "Accept": "text/event-stream",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Host": "open.zju.edu.cn",
            "Origin": "https://open.zju.edu.cn",
            "Referer": f"https://open.zju.edu.cn/product/llm/chat/{self.app_key}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "x-csrf-token": self.csrf令牌,
            "app-visitor-key": self._生成访客密钥()
        }

    def 发送消息(self, 消息内容: str, 流式输出: bool = True) -> Iterator[str]:
        """发送聊天消息并获取回复"""
        try:
            if self.调试模式:
                logger.debug(f"准备发送消息: {消息内容}")

            查询数据 = {
                "Query": 消息内容,
                "AppKey": self.app_key,
                "AppConversationID": self.会话ID,
                "QueryExtends": {"Files": []}
            }

            if self.调试模式:
                logger.debug(f"发送查询数据: {查询数据}")

            查询响应 = self.会话.post(
                f"{self.base_url}/api/proxy/chat/v2/chat_query",
                headers=self._获取API请求头(),
                json=查询数据,
                stream=True,
                timeout=30
            )

            if self.调试模式:
                logger.debug(f"查询响应状态码: {查询响应.status_code}")
                logger.debug(f"查询响应头: {dict(查询响应.headers)}")

            查询响应.raise_for_status()

            # 直接处理流式响应
            for line in 查询响应.iter_lines():
                if not line:
                    continue
                    
                try:
                    line = line.decode('utf-8')
                except UnicodeDecodeError:
                    continue

                if self.调试模式:
                    logger.debug(f"收到数据: {line}")
                    
                if line.startswith("data:"):
                    try:
                        # 处理 "data:data:" 前缀
                        数据文本 = line.replace("data:data:", "data:").replace("data:", "").strip()
                        if not 数据文本:
                            continue
                            
                        json数据 = json.loads(数据文本)
                        
                        # 检查是否是消息事件
                        if json数据.get("event") == "message":
                            回复 = json数据.get("answer", "")
                            if 回复:
                                yield 回复
                                
                    except json.JSONDecodeError as e:
                        if self.调试模式:
                            logger.warning(f"JSON解析失败: {e}")
                        continue

        except Exception as e:
            logger.error(f"发送消息失败: {str(e)}")
            if self.调试模式:
                logger.exception("详细错误信息")
            raise

    def _处理普通响应(self, 响应: requests.Response) -> str:
        """处理非流式响应"""
        完整响应 = ""
        for 片段 in self._处理流式响应(响应):
            完整响应 += 片段
        return 完整响应

    def _处理流式响应(self, 响应: requests.Response) -> Iterator[str]:
        """处理流式响应数据"""
        try:
            for line in 响应.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if self.调试模式:
                        logger.debug(f"收到原始数据: {line}")
                    
                    if line.startswith("data:"):
                        数据 = line[5:].strip()
                        if 数据:
                            try:
                                json数据 = json.loads(数据)
                                if "MessageInfo" in json数据:
                                    内容 = json数据["MessageInfo"]["AnswerInfo"]["Answer"]
                                    if 内容:
                                        if self.调试模式:
                                            logger.debug(f"解析到回复内容: {内容}")
                                        yield 内容
                            except json.JSONDecodeError as e:
                                logger.warning(f"JSON解析失败: {str(e)}")
                                continue
        except Exception as e:
            logger.error(f"流式响应处理错误: {str(e)}")
            raise

    def _生成访客密钥(self) -> str:
        """生成访客密钥"""
        密钥 = f"cv{uuid.uuid4().hex[:18]}"
        if self.调试模式:
            logger.debug(f"生成访客密钥: {密钥}")
        return 密钥

    def _生成会话ID(self) -> str:
        """生成会话ID"""
        会话id = f"cv{uuid.uuid4().hex[:18]}"
        if self.调试模式:
            logger.debug(f"生成会话ID: {会话id}")
        return 会话id

    def _生成CSRF令牌(self) -> str:
        """生成CSRF令牌"""
        令牌 = f"{uuid.uuid4().hex[:24]}"
        if self.调试模式:
            logger.debug(f"生成CSRF令牌: {令牌}")
        return 令牌

    def _生成消息ID(self) -> str:
        """生成消息ID"""
        message_id = f"01{uuid.uuid4().hex[:28].upper()}"
        if self.调试模式:
            logger.debug(f"生成消息ID: {message_id}")
        return message_id

    def _获取基础请求头(self) -> dict:
        """获取基础请求头"""
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Host": "open.zju.edu.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0",
            "sec-ch-ua": '"Not(A:Brand";v="99", "Microsoft Edge";v="133", "Chromium";v="133"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"'
        }

    def _获取聊天请求头(self) -> dict:
        """获取聊天专用请求头"""
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "ApiKey": "",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Host": "open.zju.edu.cn",
            "Origin": "https://open.zju.edu.cn",
            "Referer": f"https://open.zju.edu.cn/product/llm/chat/{self.app_key}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0",
            "app-visitor-key": self._生成访客密钥(),
            "sec-ch-ua": '"Not(A:Brand";v="99", "Microsoft Edge";v="133", "Chromium";v="133"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "x-csrf-token": self._生成CSRF令牌()
        } 