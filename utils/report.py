def save_report(content: str, filename="report.md"):
    with open(filename, "w") as f:
        f.write(content)
    print(f"\n[+] 报告已保存至 {filename}")
