from flask import Flask
import subprocess
import os

app = Flask(__name__)

@app.route("/")
def home():
    return '<button onclick="window.location.href=\'/run\'">Run Script</button>'

@app.route("/run")
def run_script():
    env = os.environ.copy()
    result = subprocess.run(
        ["python", "myscript.py"],
        capture_output=True,
        text=True,
        env=env
    )
    return f"<pre>{result.stdout or result.stderr}</pre>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
