import sys
from datetime import datetime 
import numpy as np

def parse_file(file_name:str, client_hostname:str):
    latencies = []
    with open(file_name) as file:
        lines = [line.rstrip() for line in file]
        i = 0
        while len(lines) > 0:
            line = lines[i]
            # print("line=", line)
            if line.strip():
                time = line[0:15]
                # print("time=", time)
                sender_and_reciever = line[line.index("IP")+3:line.index(": ")].split(" > ")
                if client_hostname in sender_and_reciever[0]:
                    # print("sender_and_reciever = ", sender_and_reciever)
                    j = i + 1
                    while j < len(lines):
                        line_two = lines[j]
                        if line_two.strip():
                            time_two = line_two[0:15]
                            sender_and_reciever_two = line_two[line_two.index("IP")+3:line_two.index(": ")].split(" > ")
                            if sender_and_reciever[0] == sender_and_reciever_two[1] and sender_and_reciever[1] == sender_and_reciever_two[0]:
                                time_elapsed = datetime.strptime(time_two,"%H:%M:%S.%f") - datetime.strptime(time, "%H:%M:%S.%f")
                                latencies.append(time_elapsed.total_seconds()*1000)
                                lines.remove(line_two)
                                break
                        j += 1
            lines.remove(line)
    return {"latencies": latencies, "percentiles": np.percentile(latencies, [50,75,90,99,99.9,99.99,99.999,100])}