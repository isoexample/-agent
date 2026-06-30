import streamlit as st
import sys, os
from io import StringIO
from dotenv import load_dotenv
from agent.core import run_pentest
from utils.report import save_report
from utils.html_report import save_html_report

load_dotenv()  # 加载 .env 作为默认值，但会被界面输入覆盖

st.set_page_config(page_title="SecAgent", layout="wide")
st.title("🔐 SecAgent - 自主渗透测试智能体")

# ---- 侧边栏：API 配置 ----
with st.sidebar:
    st.header("⚙️ API 配置")
    # 如果 .env 中有 Key，就用它作为默认值，否则留空
    default_key = os.getenv("OPENAI_API_KEY", "")
    api_key = st.text_input(
        "DeepSeek API Key",
        value=default_key,
        type="password",
        help="在此输入你的 DeepSeek API Key，不会存储到服务器。也可以留空使用 .env 文件中的 Key。"
    )
    if st.button("应用 Key"):
        st.session_state["api_key"] = api_key
        st.success("API Key 已更新！")
    # 如果 session_state 中有之前设置的 Key，就用它；否则用输入框的值
    active_key = st.session_state.get("api_key", api_key)

# ---- 主界面 ----
st.markdown("输入授权测试目标，观察 AI 自动进行侦察、漏洞发现和利用")

target = st.text_input(
    "目标 URL 或 IP",
    value="http://localhost/DVWA/vulnerabilities/sqli/?id=1&Submit=Submit"
)

cookie_input = st.text_input(
    "自定义 Cookie（可选，用于认证）",
    placeholder="PHPSESSID=xxx; security=low"
)
if cookie_input:
    os.environ["TARGET_COOKIE"] = cookie_input

if st.button("开始测试") and target:
    if not active_key:
        st.error("请在左侧输入 DeepSeek API Key，或在 .env 文件中配置 OPENAI_API_KEY")
        st.stop()

    output_buffer = StringIO()
    old_stdout = sys.stdout
    sys.stdout = output_buffer

    status = st.info("正在执行渗透测试...")

    try:
        # 传入 active_key 给 run_pentest
        final_output, tool_history = run_pentest(target, api_key=active_key)
        sys.stdout = old_stdout

        log_text = output_buffer.getvalue()
        with st.expander("查看详细执行日志", expanded=True):
            st.code(log_text, language="bash")

        save_report(final_output)
        save_html_report(final_output, tool_history=tool_history)

        st.success("测试完成！")
        st.markdown("## 📝 渗透测试报告")
        st.markdown(final_output)

        with open("report.html", "r") as f:
            html_content = f.read()
        st.download_button(
            "下载 HTML 报告",
            html_content,
            file_name="report.html",
            mime="text/html"
        )

    except Exception as e:
        sys.stdout = old_stdout
        st.error(f"运行出错: {e}")
