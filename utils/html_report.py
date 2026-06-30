import markdown

def save_html_report(markdown_text: str, tool_history: list = None, filename="report.html"):
    html_body = markdown.markdown(markdown_text, extensions=['tables', 'fenced_code'])
    
    # 生成 Mermaid 攻击路径图
    mermaid_chart = ""
    if tool_history:
        # 去重相邻重复项（如连续多次调用同一工具）
        cleaned = []
        for t in tool_history:
            if not cleaned or t != cleaned[-1]:
                cleaned.append(t)
        nodes = "\n".join([f"        {t}[{t}]" for t in cleaned])
        arrows = "\n".join([f"        {cleaned[i]} --> {cleaned[i+1]}" for i in range(len(cleaned)-1)])
        mermaid_chart = f"""<div class="mermaid">
graph TD
{nodes}
{arrows}
</div>
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<script>mermaid.initialize({{startOnLoad:true}});</script>"""
    
    html_template = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SecAgent 渗透测试报告</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #f9f9f9; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        h1 {{ color: #d9534f; border-bottom: 3px solid #d9534f; padding-bottom: 10px; }}
        h2 {{ color: #5bc0de; border-bottom: 1px solid #ccc; padding-bottom: 5px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th {{ background: #d9534f; color: white; padding: 10px; text-align: left; }}
        td {{ border: 1px solid #ddd; padding: 8px; }}
        code {{ background: #2d2d2d; color: #f8f8f2; padding: 2px 5px; border-radius: 4px; }}
        pre {{ background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 8px; overflow-x: auto; }}
        .severity-high {{ color: #d9534f; font-weight: bold; }}
        .footer {{ margin-top: 30px; color: #777; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        {mermaid_chart}
        {html_body}
        <div class="footer">报告由 SecAgent AI 自动生成</div>
    </div>
</body>
</html>"""
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"\n[+] HTML 报告已保存至 {filename}")
