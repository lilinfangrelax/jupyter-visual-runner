import re

def format_jupyter_traceback(traceback_lines):
    """
    清理ANSI转义码并合并traceback列表为字符串
    """
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    cleaned = [ansi_escape.sub('', line) for line in traceback_lines]
    return '\n'.join(cleaned)