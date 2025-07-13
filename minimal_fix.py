import subprocess
import re
import json
from pathlib import Path

class MinimalFixExtension:
    """
    1) Runs your shell/python command once.
    2) If it fails with a NameError, injects `missing_name = None` at the top of that script.
    3) Records that fix to fix_memory.json and retries once.
    """

    name = "name_error_fixer"
    description = (
        "Catches NameError in stderr, patches missing names as None, and retries once."
    )

    def __init__(self, memory_path="fix_memory.json"):
        self.memory_path = Path(memory_path)
        if self.memory_path.exists():
            self.memory = json.loads(self.memory_path.read_text(encoding="utf-8"))
        else:
            self.memory = []

    def run(self, command: str, **kwargs) -> str:
        # 1) First attempt
        proc = subprocess.run(command, shell=True, capture_output=True, text=True)
        if proc.returncode == 0:
            return proc.stdout + proc.stderr

        # combine outputs so far
        output = proc.stdout + proc.stderr
        stderr = proc.stderr or proc.stdout

        # 2) Look for a Python NameError
        m = re.search(r"NameError: name '(\w+)' is not defined", stderr)
        if not m:
            return output

        missing = m.group(1)
        parts = command.split()

        # only auto-patch simple `python script.py` calls
        if len(parts) >= 2 and parts[0] == "python":
            script = Path(parts[1])
            if script.exists():
                # prepend `missing = None`
                header = f"{missing} = None\n"
                original = script.read_text(encoding="utf-8")
                script.write_text(header + original, encoding="utf-8")

                # record this fix
                self.memory.append({"script": str(script), "fix": header})
                self.memory_path.write_text(
                    json.dumps(self.memory, indent=2), encoding="utf-8"
                )

                # 3) retry once
                proc2 = subprocess.run(command, shell=True, capture_output=True, text=True)
                return proc2.stdout + proc2.stderr

        # fallback: return the original failure output
        return output
