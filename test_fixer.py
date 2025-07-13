from minimal_fix import MinimalFixExtension
# ensure a fresh memory file
import os
if os.path.exists("fix_memory.json"):
    os.remove("fix_memory.json")

# write a tiny crash script
with open("crash.py","w") as f:
    f.write("print(missing_var)\n")

fixer = MinimalFixExtension(memory_path="fix_memory.json")
out = fixer.run("python crash.py")
print("=== fixer output ===")
print(out)
print("=== memory file ===")
print(open("fix_memory.json").read())
