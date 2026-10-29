
import ast

def detect_bug(code):
    try:
        ast.parse(code)
        return {
            "error": "No syntax error found",
            "suggestion": "Python syntax is correct.",
            "fixed_code": code
        }
    except SyntaxError as e:
        return {
            "error": "Syntax Error",
            "suggestion": f"Line {e.lineno}: {e.msg}",
            "fixed_code": code
        }