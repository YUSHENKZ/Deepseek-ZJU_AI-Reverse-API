from flask import Flask, request, Response, stream_with_context
import json
import time
import logging
from core.chat_api import ZJU_AI聊天API
from core.config import Config
import os

logger = logging.getLogger(__name__)

class API服务器:
    def __init__(self, 调试模式: bool = False):
        self.app = Flask(__name__)
        self.聊天api = ZJU_AI聊天API(调试模式=调试模式)
        self.config = Config()
        self.设置路由()
        # 添加打字机效果的延迟时间（秒）
        self.字符延迟 = 0.027  # 每个字符的延迟时间

    def 验证密钥(self):
        """验证API密钥"""
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return False
        api_key = auth_header.replace('Bearer ', '')
        return self.config.is_valid_key(api_key)

    def 设置路由(self):
        @self.app.route("/v1/chat/completions", methods=["POST"])
        def chat_completions():
            if not self.验证密钥():
                return self._错误响应("无效的API密钥", 401)

            try:
                数据 = request.json
                模型名称 = 数据.get("model", "")
                
                # 验证模型名称
                if not self.config.is_valid_model(模型名称):
                    return self._错误响应(
                        f"模型 '{模型名称}' 不可用，请使用 '{self.config.model_name}'",
                        404,
                        "invalid_request_error",
                        "model_not_found"
                    )

                消息列表 = 数据.get("messages", [])
                流式输出 = 数据.get("stream", True)

                if not 消息列表:
                    return self._错误响应("未提供消息", 400)

                # 获取最后一条消息的内容
                最后消息 = 消息列表[-1].get("content", "")
                if isinstance(最后消息, list):
                    # 如果是列表格式（包含文件），提取纯文本内容
                    文本内容 = []
                    for item in 最后消息:
                        if isinstance(item, dict) and item.get("type") == "text":
                            文本内容.append(item.get("text", ""))
                    最后消息 = " ".join(文本内容)

                def 生成响应():
                    try:
                        完整响应 = ""
                        for 片段 in self.聊天api.发送消息(最后消息):
                            if 流式输出:
                                for 字符 in 片段:
                                    完整响应 += 字符
                                    响应数据 = {
                                        "id": "chatcmpl-" + 最后消息[:6],
                                        "object": "chat.completion.chunk",
                                        "created": int(time.time()),
                                        "model": self.config.model_name,
                                        "choices": [{
                                            "delta": {
                                                "content": 字符
                                            },
                                            "index": 0,
                                            "finish_reason": None
                                        }]
                                    }
                                    yield f"data: {json.dumps(响应数据, ensure_ascii=False)}\n\n"
                                    time.sleep(self.字符延迟)
                        
                        if 流式输出:
                            结束数据 = {
                                "id": "chatcmpl-" + 最后消息[:6],
                                "object": "chat.completion.chunk",
                                "created": int(time.time()),
                                "model": self.config.model_name,
                                "choices": [{
                                    "delta": {},
                                    "index": 0,
                                    "finish_reason": "stop"
                                }]
                            }
                            yield f"data: {json.dumps(结束数据, ensure_ascii=False)}\n\n"
                            yield "data: [DONE]\n\n"
                    except Exception as e:
                        error_data = {
                            "error": {
                                "message": str(e),
                                "type": "server_error",
                                "code": 500
                            }
                        }
                        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
                        yield "data: [DONE]\n\n"

                if 流式输出:
                    return Response(
                        stream_with_context(生成响应()),
                        content_type='text/event-stream',
                        headers={
                            'Cache-Control': 'no-cache',
                            'X-Accel-Buffering': 'no'
                        }
                    )
                else:
                    try:
                        完整响应 = ""
                        for 片段 in self.聊天api.发送消息(最后消息):
                            完整响应 += 片段
                        
                        return {
                            "id": "chatcmpl-" + 最后消息[:6],
                            "object": "chat.completion",
                            "created": int(time.time()),
                            "model": self.config.model_name,
                            "choices": [{
                                "message": {
                                    "role": "assistant",
                                    "content": 完整响应
                                },
                                "index": 0,
                                "finish_reason": "stop"
                            }]
                        }
                    except Exception as e:
                        return self._错误响应(str(e), 500)

            except Exception as e:
                return self._错误响应(str(e), 500)

        @self.app.route("/v1/models", methods=["GET"])
        def list_models():
            if not self.验证密钥():
                return {"error": "无效的API密钥"}, 401

            return {
                "object": "list",
                "data": [{
                    "id": self.config.model_name,
                    "object": "model",
                    "created": 1677610602,
                    "owned_by": "zju"
                }]
            }

    def _错误响应(self, 消息: str, 状态码: int, 错误类型: str = "server_error", 错误代码: str = None) -> tuple:
        """生成标准错误响应"""
        错误数据 = {
            "error": {
                "message": 消息,
                "type": 错误类型
            }
        }
        if 错误代码:
            错误数据["error"]["code"] = 错误代码
        return 错误数据, 状态码

    def 运行(self, host: str = '0.0.0.0', port: int = 8000):
        """运行API服务器"""
        if os.getenv('FLASK_ENV') == 'production':
            try:
                # 生产环境尝试使用 gunicorn
                import gunicorn.app.base
                
                class StandaloneApplication(gunicorn.app.base.BaseApplication):
                    def __init__(self, app, options=None):
                        self.options = options or {}
                        self.application = app
                        super().__init__()

                    def load_config(self):
                        for key, value in self.options.items():
                            self.cfg.set(key.lower(), value)

                    def load(self):
                        return self.application

                options = {
                    'bind': f'{host}:{port}',
                    'workers': 4,
                    'worker_class': 'sync',
                    'timeout': 120,
                    'accesslog': '-',
                    'errorlog': '-'
                }
                
                StandaloneApplication(self.app, options).run()
            except ImportError:
                # 如果无法导入 gunicorn（Windows环境），使用 waitress
                try:
                    from waitress import serve
                    logger.info("在Windows环境下使用waitress服务器")
                    serve(self.app, host=host, port=port)
                except ImportError:
                    logger.warning("未安装生产环境服务器，使用Flask开发服务器")
                    self.app.run(host=host, port=port)
        else:
            # 开发环境使用 Flask 内置服务器
            self.app.run(host=host, port=port) 