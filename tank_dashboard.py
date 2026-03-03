from flask import Flask, render_template_string, jsonify, request
import threading
import time
from datetime import datetime

app = Flask(__name__)

# Tank Settings (Realistic)
TANK_CAPACITY = 1000  # liters
water_level = 300     # starting liters
pump_flow_rate = 40   # liters per minute
motor_on = False
mode = "AUTO"
history = []

def get_usage_rate():
    """Simulate different water usage based on time of day"""
    hour = datetime.now().hour

    if 6 <= hour <= 9:      # Morning rush
        return 25
    elif 18 <= hour <= 21:  # Evening usage
        return 20
    else:
        return 5            # Low usage

def simulate_tank():
    global water_level, motor_on, history, mode

    while True:
        usage = get_usage_rate() / 60  # convert per minute to per second
        fill = pump_flow_rate / 60     # pump per second

        if mode == "AUTO":
            if water_level <= 200:
                motor_on = True
            if water_level >= 950:
                motor_on = False

        if motor_on:
            water_level += fill

        water_level -= usage

        water_level = max(0, min(TANK_CAPACITY, water_level))

        history.append(water_level)
        history[:] = history[-30:]

        time.sleep(1)

thread = threading.Thread(target=simulate_tank)
thread.daemon = True
thread.start()

@app.route("/")
def dashboard():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smart Water Tank</title>
        <style>
            body { font-family: Arial; text-align:center; background:#f4f6f8; }
            .card { background:white; padding:20px; margin:20px auto; width:500px;
                    border-radius:10px; box-shadow:0 4px 10px rgba(0,0,0,0.1);}
            button { padding:10px 20px; margin:5px; border:none;
                     border-radius:5px; cursor:pointer; }
            .on { background:green; color:white; }
            .off { background:red; color:white; }
            .auto { background:blue; color:white; }
            .alert { padding:10px; margin:10px; border-radius:5px; }
            .full { background:#ffcccc; }
            .low { background:#fff3cd; }
        </style>

        <script>
            async function updateData() {
                const response = await fetch('/data');
                const data = await response.json();

                document.getElementById("liters").innerText = data.liters.toFixed(1) + " L";
                document.getElementById("percent").innerText = data.percent + "%";
                document.getElementById("motor").innerText = data.motor;
                document.getElementById("mode").innerText = data.mode;

                let alertBox = document.getElementById("alert");

                if (data.percent >= 95) {
                    alertBox.innerText = "🚨 Tank Almost Full!";
                    alertBox.className = "alert full";
                } else if (data.percent <= 20) {
                    alertBox.innerText = "⚠ Tank Low!";
                    alertBox.className = "alert low";
                } else {
                    alertBox.innerText = "";
                    alertBox.className = "";
                }

                let canvas = document.getElementById("chart");
                let ctx = canvas.getContext("2d");
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                let values = data.history;
                let width = canvas.width;
                let height = canvas.height;

                ctx.beginPath();
                ctx.moveTo(0, height - (values[0]/10));

                for (let i = 1; i < values.length; i++) {
                    ctx.lineTo(i * (width / values.length), height - (values[i]/10));
                }

                ctx.stroke();
            }

            async function toggleMotor(state) {
                await fetch('/motor', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({state: state})
                });
            }

            async function setAuto() {
                await fetch('/auto', {method: 'POST'});
            }

            setInterval(updateData, 1000);
        </script>
    </head>
    <body>

        <div class="card">
            <h1>💧 Realistic Smart Tank</h1>
            <h2>Water: <span id="liters"></span></h2>
            <h3>Level: <span id="percent"></span></h3>
            <h3>Motor: <span id="motor"></span></h3>
            <h3>Mode: <span id="mode"></span></h3>

            <div id="alert"></div>

            <button class="on" onclick="toggleMotor(true)">Manual ON</button>
            <button class="off" onclick="toggleMotor(false)">Manual OFF</button>
            <button class="auto" onclick="setAuto()">Auto Mode</button>

            <h3>Water History</h3>
            <canvas id="chart" width="450" height="200"></canvas>
        </div>

    </body>
    </html>
    """)

@app.route("/data")
def data():
    percent = int((water_level / TANK_CAPACITY) * 100)
    return jsonify({
        "liters": water_level,
        "percent": percent,
        "motor": "ON ⚡" if motor_on else "OFF 🛑",
        "mode": mode,
        "history": history
    })

@app.route("/motor", methods=["POST"])
def motor():
    global motor_on, mode
    mode = "MANUAL"
    motor_on = request.json["state"]
    return jsonify({"status": "ok"})

@app.route("/auto", methods=["POST"])
def auto():
    global mode
    mode = "AUTO"
    return jsonify({"status": "auto mode enabled"})

if __name__ == "__main__":
    app.run(debug=True)