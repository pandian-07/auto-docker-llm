import sys
import os

from scanner.detect_stack import detect_stack
from llm.dockerfile_prompt import build_prompt
from generator.generate_dockerfile import generate_dockerfile

if len(sys.argv) != 2:
    print("Usage: python main.py <project_path>")
    sys.exit(1)

project_path = sys.argv[1]

if not os.path.isdir(project_path):
    print("❌ Invalid project path")
    sys.exit(1)

stack = detect_stack(project_path)
print(f"[+] Detected Tech Stack: {stack}")

if stack == "unknown":
    print("❌ Unsupported project type")
    sys.exit(1)

prompt = build_prompt(stack)
dockerfile_content = generate_dockerfile(prompt)

dockerfile_path = os.path.join(project_path, "Dockerfile")
with open(dockerfile_path, "w") as f:
    f.write(dockerfile_content)

print(f"[✔] Dockerfile generated successfully at {dockerfile_path}")

