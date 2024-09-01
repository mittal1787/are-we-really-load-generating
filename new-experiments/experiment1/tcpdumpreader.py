import subprocess as sub
import sys
import time
import os
import signal

p = sub.Popen(('sh', 'tcpdumpreader.sh', sys.argv[1]), stdout=sub.PIPE)

t_end = time.time() + 60
for stdout_line in iter(p.stdout.readline, ""):
    print(stdout_line.decode("UTF-8"))
    if time.time() >= t_end:
        break
os.killpg(os.getpgid(p.pid), signal.SIGTERM)