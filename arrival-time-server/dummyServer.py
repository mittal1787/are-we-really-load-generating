from flask import Flask
import time

app = Flask(__name__)
time_map = {}
f = open('timestamp.txt', 'w')
@app.route("/")
def hello_world():
    arrival_time = time.time()
    f = open("timestamp.txt","a")
    print(arrival_time)
    print(arrival_time,file=f)
    f.close()
    return "1"

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8080,debug=True, threaded=True)