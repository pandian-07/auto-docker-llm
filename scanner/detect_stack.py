import os

def detect_stack(project_path):
    for root, dirs, files in os.walk(project_path):
        if "package.json" in files:
            return "node"
        if "requirements.txt" in files:
            return "python"
        if "pom.xml" in files:
            return "java"
        if "go.mod" in files:
            return "go"

    return "unknown"

