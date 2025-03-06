import click
import logging
import time
import sys
from core.chat_api import ZJU_AI聊天API

logger = logging.getLogger(__name__)

class 命令行模式:
    def __init__(self, 调试模式: bool = False):
        self.聊天api = ZJU_AI聊天API(调试模式=调试模式)

    def 启动(self):
        """启动命令行聊天模式"""
        click.echo("启动聊天会话 (输入 'quit' 退出)...")
        
        while True:
            try:
                用户输入 = click.prompt('你')
                if 用户输入.lower() == 'quit':
                    break
                    
                click.echo('助手: ', nl=False)
                for 片段 in self.聊天api.发送消息(用户输入):
                    sys.stdout.write(片段)
                    sys.stdout.flush()
                    time.sleep(0.05)  # 控制打字速度
                click.echo()
                
            except Exception as e:
                logger.error(f"聊天错误: {str(e)}")
                click.echo(f"\n错误: {str(e)}")
                if click.confirm('是否继续?', default=True):
                    continue
                break 