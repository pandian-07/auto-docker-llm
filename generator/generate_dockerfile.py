import subprocess

def generate_dockerfile(prompt):
    result = subprocess.run(
        ["ollama", "run", "llama3"],
        input=prompt.encode("utf-8"),   # ✅ encode input
        capture_output=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Ollama failed: {result.stderr.decode('utf-8', errors='ignore')}"
        )

    # ✅ decode output safely
    return result.stdout.decode("utf-8", errors="ignore").strip()
def generate_dockerfile(prompt: str) -> str:
    # Prompt already contains the final Dockerfile
    return prompt.strip()

