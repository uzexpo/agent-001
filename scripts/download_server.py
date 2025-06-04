from flask import Flask, send_from_directory
import os

app = Flask(__name__)
AGENT_FILE = os.getenv("AGENT_ZIP_PATH", "release/agent_package.zip")

@app.route("/")
def index():
    return "<h1>AI Agent Download</h1><p><a href='/download'>Download here</a></p>"

@app.route("/download")
def download():
    directory = os.path.dirname(AGENT_FILE)
    filename = os.path.basename(AGENT_FILE)
    return send_from_directory(directory, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
