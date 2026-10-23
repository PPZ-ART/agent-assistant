# Agent 工具调用助手

一个能自主调用工具的 AI Agent：AI 根据问题决定用哪个工具，执行后再总结回答。

## 内置工具

| 工具 | 作用 |
|---|---|
| get_weather | 查询城市实时天气（wttr.in） |
| calculate | 计算数学表达式 |
| read_file | 读取本地文本文件 |

## 运行方法

1. 设置环境变量 `DEEPSEEK_KEY`
2. 运行 `python main.py`

## 工作流程

1. 用户提问
2. 把问题 + 工具列表发给 DeepSeek
3. AI 返回要调用的工具和参数
4. 本地执行工具，把结果回传给 AI
5. AI 基于工具结果生成最终回答

## 技术栈

- Python 3.12
- DeepSeek API（function calling）
- urllib / json
