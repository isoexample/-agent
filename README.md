# 🔐 SecAgent — AI 自主渗透测试智能体

> 基于 **LLM（DeepSeek）** 的自动化渗透测试 Agent，输入目标 URL 即可自动完成侦察、漏洞扫描和 SQL 注入利用，生成专业双格式报告。

## ✨ 功能亮点

- 🤖 **自主决策**：AI 自动规划攻击路径，零人工干预
- 🧰 **真实工具链**：集成 `nmap`、`gobuster`、`nikto`、`sqlmap`
- 🔓 **自动登录**：针对 DVWA 等靶场自动获取 Session
- 📊 **双格式报告**：Markdown + HTML（含 **Mermaid 攻击路径图**）
- 🌐 **Web 界面**：Streamlit 面板，输入 API Key 和目标即可测试
- 🧪 **多靶场支持**：本地 DVWA、sqli-labs 等（可扩展）

## 🏗️ 架构
用户输入 (URL) → Agent 规划 → 调用工具 (nmap/nikto/gobuster/sqlmap)
↓
记录工具调用链 → 生成 Markdown 报告
↓
渲染 HTML + Mermaid 攻击路径图

text

## 🚀 快速开始

### 环境要求
- Ubuntu 20.04/22.04
- Python 3.10+
- 系统工具：nmap、gobuster、nikto、sqlmap

### 1. 安装依赖
```bash
pip install -r requirements.txt
2. 获取 DeepSeek API Key
注册 DeepSeek 开放平台(后续可能做别的大模型，目前就是做着测试用)

创建 API Key，新用户免费送 500 万 tokens

3. 启动 Web 界面
bash
python3 -m streamlit run app.py
浏览器打开 http://localhost:8501，在左侧边栏粘贴 API Key，输入目标 URL 即可开始。

也可以选择命令行模式（需先配置 .env）：

bash
cp .env.example .env   # 编辑 .env 填入 Key
python3 main.py
🎯 测试案例
靶场	测试 URL	结果
DVWA (Low)	http://localhost/DVWA/vulnerabilities/sqli/?id=1&Submit=Submit	✅ 自动登录 → 拖库
DVWA (Low)	http://localhost/DVWA/vulnerabilities/sqli_blind/?id=1&Submit=Submit	✅ 盲注检测 → 枚举数据库
sqli-labs	http://localhost/sqli-labs/Less-1/?id=1	✅ 无 Cookie 直接注入
⚠️ 免责声明
本项目仅用于合法授权的安全测试和教育目的。使用者必须确保拥有对测试目标的明确书面授权，否则后果自负。开发者不承担任何因滥用本项目造成的法律责任。

📄 许可证
MIT License


