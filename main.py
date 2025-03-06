import os
import logging
from dotenv import load_dotenv
from modes.api_mode import API服务器
from modes.cli_mode import 命令行模式

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def 运行程序():
    """根据配置文件运行指定模式"""
    try:
        # 加载运行配置
        load_dotenv('run_config.env')
        
        # 获取运行模式
        运行模式 = os.getenv('RUN_MODE', 'api').lower()
        
        if 运行模式 == 'api':
            # API服务器模式
            主机名 = os.getenv('API_HOST', '0.0.0.0')
            端口 = int(os.getenv('API_PORT', '8000'))
            调试模式 = os.getenv('API_DEBUG', 'false').lower() == 'true'
            
            logger.info(f"启动API服务器 - 主机:{主机名} 端口:{端口} 调试:{调试模式}")
            服务器 = API服务器(调试模式=调试模式)
            服务器.运行(host=主机名, port=端口)
            
        elif 运行模式 == 'cli':
            # 命令行模式
            调试模式 = os.getenv('CLI_DEBUG', 'false').lower() == 'true'
            
            logger.info(f"启动命令行模式 - 调试:{调试模式}")
            命令行 = 命令行模式(调试模式=调试模式)
            命令行.运行()
            
        else:
            logger.error(f"未知的运行模式: {运行模式}")
            print(f"错误: 未知的运行模式 '{运行模式}'")
            print("支持的模式: api, cli")
            
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}")
        if os.getenv('API_DEBUG', 'false').lower() == 'true':
            logger.exception("详细错误信息")
        raise

if __name__ == '__main__':
    运行程序() 