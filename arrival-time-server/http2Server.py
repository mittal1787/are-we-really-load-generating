from quart import Quart, render_template, websocket
import time

app = Quart(__name__)

time_map = {}
f = open('timestamp.txt', 'w')
@app.route("/")
def hello_world():
    arrival_time = time.time()
    f = open("timestamp.txt","a")
    print(arrival_time,file=f)
    f.close()
    return "1"

@app.route("/dummy")
def dummy_work():
    arrival_time = time.time()
    f = open("timestamp.txt","a")
    print(arrival_time)
    print(arrival_time,file=f)
    f.close()
    num = 1
    for i in range(1,100):
        for j in range(1,100):
            num *= i*j
    return "1"

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8000,debug=True, threaded=True)
