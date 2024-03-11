from glob import glob
import os
from os import path

with open("scaling-wrk2.csv", "w+") as f:
    f.write("connections,threads,RPS\n")
    for filename in glob("data-wrk2/*"):
        t, c = list(map(lambda x: x[1:], path.basename(filename).split(".")[0].split("-")))
        with open(filename, "r") as data_f:
            content = data_f.read()
        rps = float("nan")
        try:
            rps = float(content.split("\n")[-3].split(":")[-1])
        except:
            pass

        f.write(f"{c},{t},{rps}\n")
