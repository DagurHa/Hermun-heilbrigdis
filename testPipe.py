import subprocess
import json

d = {
    "Hundur" : 12,
    "Kottur" : 3
    }
d_pipe = json.dumps(d)

res = subprocess.run(["./SimProj/bin/Debug/net7.0/SimProj.exe",d_pipe],capture_output=True,text=True)

out = res.stdout.strip()
print(out)