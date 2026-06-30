import subprocess

def run_tool(command: str, timeout=120):
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=timeout
        )
        if result.returncode == 0:
            return result.stdout
        else:
            return f"[Error] return code {result.returncode}:\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return "[Error] Command timed out"
    except Exception as e:
        return f"[Error] {str(e)}"
