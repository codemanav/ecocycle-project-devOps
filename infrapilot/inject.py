"""Fault injection for demo scenarios. Usage: python inject.py A|B|C|reset"""
import os, sys, subprocess, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
def sh(*a): return subprocess.run(a, capture_output=True, text=True).stdout
def reset():
    for c in ["users-db", "marketplace-service"]:
        sh("docker", "unpause", c)
    # recreate from compose to drop injected memory limits / restart policy
    subprocess.run(["docker", "compose", "up", "-d", "--force-recreate", "marketplace"],
                   cwd=ROOT, env={**os.environ, "DB_PASSWORD": "ecocycle"}, capture_output=True)
    subprocess.run(["docker", "compose", "up", "-d"], cwd=ROOT, env={**os.environ, "DB_PASSWORD": "ecocycle"}, capture_output=True)
def inject(s):
    if s == "A": sh("docker", "stop", "users-db")
    elif s == "B":
        sh("docker", "update", "--restart", "on-failure", "--memory", "100m", "--memory-swap", "100m", "marketplace-service")
        sh("docker", "restart", "marketplace-service")
    elif s == "C": sh("docker", "pause", "marketplace-service")
    elif s == "reset": reset()
if __name__ == "__main__": inject(sys.argv[1])
