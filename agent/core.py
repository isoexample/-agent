import json, os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage
from .tools import TOOLS

TOOL_MAP = {tool.name: tool for tool in TOOLS}

def run_pentest(target: str, api_key: str = None):
    # 如果没有传入 api_key，则从环境变量读取（兼容命令行模式）
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")
    
    llm = ChatOpenAI(
        model=os.getenv("MODEL_NAME", "deepseek-chat"),
        openai_api_key=api_key,
        openai_api_base=os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1"),
        temperature=0
    )
    llm_with_tools = llm.bind_tools(TOOLS)

    messages = [
        SystemMessage(content="""你是一个自主渗透测试助手，只能使用提供的工具。
任务流程：
1. 如果用户提供完整 URL（含 ?id= 参数），立即调用 sqlmap_test。
2. 如果提供 IP 或域名，先用 nmap_scan，若发现 Web 服务则用 gobuster_dir 爆破目录，再对动态页面调用 sqlmap_test。
3. 调用工具后，必须仔细阅读工具返回的全部内容，根据返回内容判断下一步：
   - 如果 sqlmap_test 返回了数据库名、表名、用户数据，测试完成，必须生成 Markdown 报告。
   - 如果工具返回错误，分析原因并重试。
4. 测试结束后，必须生成一份简洁的 Markdown 报告，包含：摘要、发现的漏洞、关键证据（注入点、数据库名、表名、用户数据）、修复建议。

规则：
- 禁止使用未提供的工具。
- 工具调用后必须处理结果，绝对不能在没有生成报告的情况下结束。
- 全程自主，无需确认。
"""),
        HumanMessage(content=f"请对目标 {target} 进行渗透测试。使用工具后必须根据工具结果继续下一步或生成报告，不得停止。")
    ]

    tool_history = []

    max_turns = 10
    for _ in range(max_turns):
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                tool_name = tool_call['name']
                tool_args = tool_call.get('args', {})
                print(f"\n[调用工具] {tool_name}, 参数: {tool_args}")
                tool_history.append(tool_name)
                tool_func = TOOL_MAP.get(tool_name)
                if tool_func:
                    try:
                        if tool_name == 'sqlmap_test':
                            url = tool_args.get('url', target)
                            result = tool_func.invoke(url)
                        elif tool_name == 'nmap_scan':
                            target_host = tool_args.get('target', target)
                            result = tool_func.invoke(target_host)
                        elif tool_name == 'gobuster_dir':
                            target_url = tool_args.get('target_url', target)
                            result = tool_func.invoke(target_url)
                        elif tool_name == 'nikto_scan':
                            target_url = tool_args.get('target_url', target)
                            result = tool_func.invoke(target_url)
                        else:
                            result = tool_func.invoke(tool_args)
                    except Exception as e:
                        result = f"工具执行出错: {str(e)}"
                    print(f"[工具返回] {result[:200]}...")
                    tool_message = ToolMessage(
                        content=result,
                        tool_call_id=tool_call['id']
                    )
                    messages.append(tool_message)
                else:
                    messages.append(ToolMessage(
                        content=f"工具 {tool_name} 不存在",
                        tool_call_id=tool_call['id']
                    ))
        else:
            print(response.content)
            return response.content, tool_history

    return "Agent 达到最大步数，仍未完成报告。", tool_history
