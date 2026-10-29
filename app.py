
from flask import Flask, render_template, request
import subprocess
import tempfile
import os
import ast

app = Flask(__name__)




def check_python(code):
    bug = detect_bug(code)

    if bug["error"] != "No syntax error found":
        return "Error Found", bug["suggestion"], bug["fixed_code"]

    try:
        result = subprocess.run(
            ["python", "-c", code],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            return "Runtime Error", result.stderr, code

        return (
            "No Error Found",
            result.stdout or "Program executed successfully.",
            code
        )

    except subprocess.TimeoutExpired:
        return "Timeout Error", "Program took too long to execute.", code
def run_code(code, language):
    try:
        with tempfile.TemporaryDirectory() as folder:

            if language == "java":
                source = os.path.join(folder, "Main.java")
                with open(source, "w", encoding="utf-8") as f:
                    f.write(code)

                compiled = subprocess.run(
                    ["javac", source],
                    capture_output=True, text=True, timeout=10
                )
                if compiled.returncode != 0:
                    return "Error Found", compiled.stderr, code

                command = ["java", "-cp", folder, "Main"]

            elif language in ("c", "cpp"):
                ext = ".c" if language == "c" else ".cpp"
                source = os.path.join(folder, "program" + ext)
                output = os.path.join(folder, "program.exe")

                with open(source, "w", encoding="utf-8") as f:
                    f.write(code)

                compiler = "gcc" if language == "c" else "g++"
                compiled = subprocess.run(
                    [compiler, source, "-o", output],
                    capture_output=True, text=True, timeout=10
                )
                if compiled.returncode != 0:
                    return "Error Found", compiled.stderr, code

                command = [output]


            
            else:
                return "Error Found", "Please select a valid language.", code

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return "Runtime Error", result.stderr or "Program failed.", code

            return "No Error Found", result.stdout or "Program executed successfully.", code

    except FileNotFoundError:
        return "Compiler Not Found", (
            f"Required compiler/interpreter for {language} is missing from PATH."
        ), code
    except subprocess.TimeoutExpired:
        return "Timeout Error", "Program took too long to execute.", code
    except Exception as e:
        return "Error Found", str(e), code


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/check", methods=["POST"])
def check_code():
    language = request.form.get("language", "python").strip().lower()
    code = request.form.get("code", "")

    if not code.strip():
        return render_template(
            "index.html",
            error="Please enter some code.",
            code=code,
            language=language
        )

    if language == "python":
        result, suggestion, fixed_code = check_python(code)
    else:
        result, suggestion, fixed_code = run_code(code, language)

    return render_template(
        "index.html",
        result=result,
        suggestion=suggestion,
        fixed_code=fixed_code,
        code=code,
        language=language
    )


if __name__ == "__main__":
    app.run(debug=True)
