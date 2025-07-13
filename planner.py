#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from urllib.request import Request, urlopen
from agent_runner import build_dev

def get_todos():
    if os.path.exists("TODO.md"):
        with open("TODO.md", "r") as f:
            return [line.strip()[2:] for line in f if line.startswith("- ")]
    else:
        url = "https://api.github.com/repos/saeed2332/saeed-replit/issues?state=open"
        req = Request(url, headers={'User-Agent': 'Planner'})
        with urlopen(req) as response:
            issues = json.loads(response.read().decode())
        return [issue['title'] for issue in issues]

def update_todos(todos):
    with open("TODO.md", "w") as f:
        for todo in todos:
            f.write(f"- {todo}\n")

def commit_push(message):
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)

if __name__ == "__main__":
    dev = build_dev()
    todos = get_todos()
    if not todos:
        print("No TODOs.")
        sys.exit(0)

    while todos:
        todo = todos[0]
        print(f"Processing: {todo}")
        dev.initiate_chat(recipient=dev, message=f"Tackle: {todo}. Fix, test, use tools.")
        dev.initiate_chat(recipient=dev, message="Review changes for improvements, edit own code if needed.")
        dev.initiate_chat(recipient=dev, message="pytest -q tests")
        if len(subprocess.run(["git", "diff", "--name-only"], capture_output=True).stdout.splitlines()) > 10:
            print("Too many changes; abort.")
            break
        commit_push(f"Completed: {todo[:50]}")
        todos = todos[1:]
        update_todos(todos)
        new_todo_resp = dev.initiate_chat(recipient=dev, message="Suggest next improvement based on this task.")
        new_todo = new_todo_resp.chat_history[-1]["content"]
        todos.append(new_todo)
    print("Done.")