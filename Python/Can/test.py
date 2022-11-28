import time
import subprocess

subProc = subprocess.Popen(["echo Hello World"], stdout=subprocess.PIPE,)
print(subProc.stdout.read())
