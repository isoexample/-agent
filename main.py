import os, traceback
from dotenv import load_dotenv
from agent.core import run_pentest
from utils.report import save_report
from utils.html_report import save_html_report

load_dotenv()

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("请先在 .env 文件中设置 OPENAI_API_KEY")
        exit(1)

    target = input("请输入测试目标 URL 或 IP (例如 http://localhost/DVWA): ")
    print(f"\n[*] 开始对 {target} 进行渗透测试...\n")

    try:
        final_output, tool_history = run_pentest(target)
        print("\n===== 最终报告 =====")
        print(final_output)
        save_report(final_output)
        print("[*] Markdown 报告已保存")
        save_html_report(final_output, tool_history=tool_history)
    except Exception as e:
        print(f"\n[!] 运行出错: {e}")
        traceback.print_exc()
