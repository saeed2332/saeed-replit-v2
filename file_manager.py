import os, json, pathlib, textwrap
from datetime import datetime

class FileManager:
    """
    Simple file-tool for an AutoGen agent.

    • list(path='.')            → JSON list of entries under path  
    • read(file, n=1000)        → first n chars of file  
    • write(file, content)      → overwrite file  
    • append(file, content)     → append to file
    """

    name = "file_manager"
    description = "List / read / write / append files in the workspace."

    # ---- helpers -------------------------------------------------
    root = pathlib.Path("/workspace/saeed-replit").resolve()

    def _resolve(self, p: str) -> pathlib.Path:
        pth = (self.root / p).resolve()
        if self.root not in pth.parents and pth != self.root:
            raise ValueError("path escapes workspace")
        return pth

    # ---- tool entrypoints ---------------------------------------
    def list(self, path="."):
        p = self._resolve(path)
        return json.dumps(sorted(os.listdir(p)))

    def read(self, file, n=10000):
        p = self._resolve(file)
        return p.read_text()[: int(n)]

    def write(self, file, content):
        p = self._resolve(file)
        p.write_text(textwrap.dedent(content), encoding="utf-8")
        return f"Wrote {p}"

    def append(self, file, content):
        p = self._resolve(file)
        with p.open("a", encoding="utf-8") as f:
            f.write(textwrap.dedent(content))
        return f"Appended to {p}"
