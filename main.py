import os
import json
import urllib.request
import urllib.parse

# ===== 配置 =====
DeepSeek密钥 = os.environ.get("DEEPSEEK_KEY")
if not DeepSeek密钥:
    print("错误：请设置 DEEPSEEK_KEY 环境变量")
    exit()

# ===== 工具实现 =====
def 查天气(city):
    地址 = "https://wttr.in/" + urllib.parse.quote(city) + "?format=3"
    with urllib.request.urlopen(地址, timeout=20) as 响应:
        return 响应.read().decode("utf-8").strip()

def 算数(expression):
    允许 = set("0123456789+-*/(). ")
    if not set(expression) <= 允许:
        return "错误：表达式只能包含数字和 + - * / ( )"
    try:
        return str(eval(expression))
    except Exception as e:
        return "计算出错：" + str(e)

def 读文件(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()[:2000]
    except Exception as e:
        return "读取失败：" + str(e)

# ===== 工具定义（告诉 AI 有哪些工具）=====
工具列表 = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的当前天气",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string", "description": "城市名，如北京"}},
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "计算数学表达式，例如 23*45+100",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string", "description": "数学表达式"}},
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取本地文本文件的内容",
            "parameters": {
                "type": "object",
                "properties": {"filename": {"type": "string", "description": "文件名，如 note.txt"}},
                "required": ["filename"],
            },
        },
    },
]

工具字典 = {"get_weather": 查天气, "calculate": 算数, "read_file": 读文件}

# ===== 调 DeepSeek =====
def 调用大模型(消息):
    数据 = json.dumps({
        "model": "deepseek-chat",
        "messages": 消息,
        "tools": 工具列表,
    }).encode("utf-8")
    请求 = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=数据,
        headers={"Authorization": "Bearer " + DeepSeek密钥, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(请求, timeout=60) as 响应:
        return json.loads(响应.read().decode("utf-8"))

# ===== Agent 循环 =====
def 运行Agent(问题):
    消息 = [
        {"role": "system", "content": "你是一个能调用工具的AI助手。需要实时信息或计算时必须调用工具，不要凭记忆编造。"},
        {"role": "user", "content": 问题},
    ]
    while True:
        结果 = 调用大模型(消息)
        AI消息 = 结果["choices"][0]["message"]

        if not AI消息.get("tool_calls"):
            return AI消息["content"]

        消息.append(AI消息)
        for 调用 in AI消息["tool_calls"]:
            工具名 = 调用["function"]["name"]
            参数 = json.loads(调用["function"]["arguments"])
            工具函数 = 工具字典.get(工具名)
            print("  [调用工具]", 工具名, 参数)
            工具结果 = 工具函数(**参数) if 工具函数 else "未知工具"
            print("  [工具返回]", str(工具结果)[:100])
            消息.append({
                "role": "tool",
                "tool_call_id": 调用["id"],
                "content": str(工具结果),
            })

# ===== 入口 =====
if __name__ == "__main__":
    print("Agent 已上线（工具：查天气 / 算数 / 读文件），输入“退出”结束")
    while True:
        问题 = input("\n你：")
        if 问题 == "退出":
            break
        print("AI：", 运行Agent(问题))
