#!/usr/bin/env python3
import subprocess

TEMPLATE = "f4b053b0171f559d7c7bcfa06c197e737dffab92"

def run(*args):
    return subprocess.check_output(args, text=True).strip()

run("git", "fetch", "origin", "main")
head = run("git", "rev-parse", "HEAD")
remote = run("git", "rev-parse", "origin/main")
assert head == remote, f"local {head} != origin/main {remote}"
subprocess.run(["git", "merge-base", "--is-ancestor", TEMPLATE, head], check=True)
url = run("git", "remote", "get-url", "origin")
assert url == "https://github.com/modelarious/recomp-index.git", url
print("REPOSITORY_PASS")
