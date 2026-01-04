import os
import sys
import shutil
import zipfile
import subprocess

# =====================================
# ADD PROJECT ROOT TO PYTHONPATH
# =====================================
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, render_template, request, jsonify

from scanner.detect_stack import detect_stack
from llm.dockerfile_prompt import build_prompt
from generator.generate_dockerfile import generate_dockerfile

# =====================================
# PATHS
# =====================================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
PROJECT_DIR = os.path.join(UPLOAD_DIR, "project")

os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)


# =====================================
# UTIL: NORMALIZE PROJECT DIR
# =====================================
def normalize_project_dir(project_dir):
    """
    If project_dir contains a single top-level folder,
    move its contents up one level.
    """
    items = os.listdir(project_dir)

    if len(items) == 1:
        inner = os.path.join(project_dir, items[0])
        if os.path.isdir(inner):
            for item in os.listdir(inner):
                shutil.move(
                    os.path.join(inner, item),
                    project_dir
                )
            shutil.rmtree(inner)


# ==============================
# UI
# ==============================
@app.route("/")
def index():
    return render_template("index.html")


# ==============================
# API: GENERATE DOCKERFILE
# ==============================
@app.route("/api/generate", methods=["POST"])
def generate():
    # Clean previous upload
    if os.path.exists(PROJECT_DIR):
        shutil.rmtree(PROJECT_DIR)

    os.makedirs(PROJECT_DIR, exist_ok=True)

    files = request.files.getlist("project")

    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    # --------------------------
    # CASE 1: ZIP upload
    # --------------------------
    if len(files) == 1 and files[0].filename.endswith(".zip"):
        zip_path = os.path.join(UPLOAD_DIR, files[0].filename)
        files[0].save(zip_path)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(PROJECT_DIR)

    # --------------------------
    # CASE 2: Folder upload
    # --------------------------
    else:
        for file in files:
            if not file.filename:
                continue

            file_path = os.path.join(PROJECT_DIR, file.filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)

    # 🔧 CRITICAL FIX
    normalize_project_dir(PROJECT_DIR)

    # Detect tech stack
    stack = detect_stack(PROJECT_DIR)
    if not stack:
        return jsonify({"error": "Unsupported project type"}), 400

    # Generate Dockerfile (deterministic)
    dockerfile_content = generate_dockerfile(build_prompt(stack))

    dockerfile_path = os.path.join(PROJECT_DIR, "Dockerfile")
    with open(dockerfile_path, "w") as f:
        f.write(dockerfile_content)

    return jsonify({
        "stack": stack,
        "dockerfile": dockerfile_content
    })


# ==============================
# API: BUILD & RUN DOCKER
# ==============================
@app.route("/api/build", methods=["POST"])
def build():
    try:
        subprocess.run(
            ["docker", "build", "-t", "autodocker-app", PROJECT_DIR],
            check=True
        )

        subprocess.run(
            ["docker", "run", "-d", "--rm", "autodocker-app"],
            check=True
        )

        return jsonify({"status": "Docker image built and container running"})

    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e)}), 500


# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    app.run(debug=True)

