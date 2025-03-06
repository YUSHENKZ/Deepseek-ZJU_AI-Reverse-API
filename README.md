# Deepseek-ZJU-Reverse-API

# ZJU_AI 逆向代理服务

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.3+-green.svg)

</div>

## 📖 项目介绍
# 前情提要：初始版本做的较为粗糙，部分文档和模块编写可能存在问题，请见谅！！
这是一个基于ZJU_AI平台的API代理服务，旨在更方便的使用该服务，请勿过度调用，支持OpenAI API格式调用。项目提供了两种运行模式：

- **API模式**: 提供兼容OpenAI格式的REST API服务
- **CLI模式**: 提供命令行交互式聊天界面

## 🏗️ 项目架构

```
├── core/                  # 核心功能模块
│   ├── chat_api.py        # ZJU_AI接口封装
│   └── config.py          # 配置管理
├── modes/                 # 运行模式实现
│   ├── api_mode.py        # API服务器模式
│   └── cli_mode.py        # 命令行模式
├── main.py                # 主程序入口
├── run_config.env         # 运行配置文件
└── requirements.txt       # 项目依赖
```

## ⚙️ 环境要求

- Python 3.8+
- 依赖包参见 `requirements.txt`

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

创建或编辑 `run_config.env` 文件（内容如下）：

```bash
# 运行模式: api 或 cli
RUN_MODE=api

# API模式配置
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# CLI模式配置
CLI_DEBUG=false
```

### 3. 配置API密钥

在环境变量或 `.env` 文件中添加API密钥配置(内容如下)：

```bash
# 模型配置
MODEL_NAME=deepseek-v3    # 调用模型名称

# API密钥配置 (格式：密钥=过期时间)
# 过期时间格式：permanent(永久) 或 YYYY-MM-DD
API_KEY_1=sk-xxxxxxxxxxxxxxxx1=permanent
API_KEY_2=sk-xxxxxxxxxxxxxxxx2=2025-12-31
API_KEY_3=sk-xxxxxxxxxxxxxxxx3=2024-06-30 
```

**格式说明：**
- `MODEL_NAME=模型名称自己设定调用的名称`
- `API_KEY_密钥序号=密钥值=过期时间`
- 过期时间可以是具体日期(YYYY-MM-DD)或`permanent`(永久有效)

### 4. 运行服务

```bash
python main.py
```

## 🔧 API使用说明

### Chat Completions API

**请求示例：**

```bash
curl http://localhost:8000/v1/chat/completions \
-H "Content-Type: application/json" \
-H "Authorization: Bearer sk-xxxxxxxx" \
-d '{
  "model": "deepseek-v3",
  "messages": [{"role": "user", "content": "你好"}],
  "stream": true
}'
```

**参数说明：**

- `model`: 模型名称(目前固定为"deepseek-v3")
- `messages`: 对话消息列表
- `stream`: 是否启用流式输出(默认true)

### Models API

```bash
curl http://localhost:8000/v1/models \
-H "Authorization: Bearer sk-xxxxxxxx"
```

## 🔒 安全说明

- 所有API请求都需要通过Bearer Token认证
- 支持API密钥过期时间设置
- 内置请求频率限制保护

## 🤝 贡献指南

欢迎提交Issue和Pull Request！在提交PR前请确保：

1. 代码符合Python代码规范
2. 新功能包含适当的测试
3. 更新相关文档

## 📄 开源许可

本项目采用 [MIT License](LICENSE) 开源许可证。

## 📞 联系方式

如有问题或建议，欢迎通过以下方式联系：

个人网站 [https://www.lic10.cn](https://www.lic10.cn))
- 发送邮件至 [1722949365xj@gmail.com](1722949365xj@gmail.com)

## 🙏 致谢

感谢ZJU_AI平台

## 结语

本项目旨在为开发者提供一个便捷的接口，以便更好地利用ZJU_AI平台的强大功能。我们欢迎任何形式的贡献和反馈，共同推动项目的进步。


# 免责声明

## 使用须知

1. **服务依赖说明**
   - 本项目是基于ZJU_AI平台的非官方接口实现
   - 不保证接口的持续可用性和稳定性
   - 上游服务的任何变更都可能影响本项目的正常运行

2. **安全与风险提示**
   - 本项目仅供学习和研究使用
   - 使用者应自行承担使用本软件产生的风险
   - 请勿用于任何违法违规用途
   - 建议在使用前备份重要数据

3. **责任限制**
   - 项目维护者不对使用本软件导致的任何直接或间接损失负责
   - 包括但不限于：
     * 数据丢失
     * 服务中断
     * 系统故障
     * 商业损失
     * 其他任何形式的损失

4. **合规要求**
   - 使用者必须遵守：
     * 中华人民共和国相关法律法规
     * ZJU_AI平台的服务条款
     * 所在地区的相关法律要求
   - 如因违反相关规定造成的后果由使用者自行承担

5. **知识产权声明**
   - 本项目代码采用MIT协议开源
   - 项目中使用的第三方依赖遵循其原有的授权协议
   - 通过本项目生成的内容版权归属需遵循ZJU_AI平台的相关规定

6. **服务保证**
   - 本项目不提供任何形式的保修、保证或条件声明
   - 不保证服务的及时性、安全性、准确性
   - 不承诺提供技术支持或产品维护

7. **隐私声明**
   - 本项目不会主动收集用户隐私信息
   - 所有对话内容均为用户与ZJU_AI平台直接交互
   - 建议用户不要在对话中透露敏感信息

## 最终解释权

- 本项目维护者保留对免责声明的最终解释权
- 使用本项目即表示您已阅读并同意本免责声明的所有内容
- 本声明未尽事宜参照相关法律法规执行
- 本免责声明可能随时更新，更新后立即生效

最后更新日期：{{2025-3-7}}


