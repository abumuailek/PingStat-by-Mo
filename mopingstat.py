import os
import platform
import subprocess
import time
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Configuration
HOSTS = ["google.com", "8.8.8.8", "8.8.4.4"]
LOG_FILE = "ping_log.csv"
PING_INTERVAL = 5  # seconds
MAX_POINTS = 100   # points shown in the graph

# Detect platform ping command
def ping(host):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    try:
        output = subprocess.check_output(['ping', param, '1', host], stderr=subprocess.DEVNULL, universal_newlines=True)
        if platform.system().lower() == 'windows':
            ms = int(output.split("Average = ")[1].split("ms")[0])
        else:
            ms = float(output.split("time=")[-1].split(" ms")[0])
        return ms
    except Exception:
        return None

# Load or initialize log
if os.path.exists(LOG_FILE):
    df = pd.read_csv(LOG_FILE)
else:
    df = pd.DataFrame(columns=["timestamp", "host", "ping_ms"])

# Store last MAX_POINTS for plot
history = {host: [] for host in HOSTS}
timestamps = []

# Set up live plot
plt.style.use("seaborn")
fig, ax = plt.subplots()
lines = {host: ax.plot([], [], label=host)[0] for host in HOSTS}
ax.set_ylim(0, 500)
ax.set_xlim(0, MAX_POINTS)
ax.set_ylabel("Ping (ms)")
ax.set_xlabel("Last {} intervals".format(MAX_POINTS))
ax.legend(loc="upper right")

def update(frame):
    global df, timestamps

    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamps.append(current_time)

    for host in HOSTS:
        ping_value = ping(host)
        print(f"[{current_time}] {host}: {ping_value if ping_value is not None else 'Timeout'} ms")
        history[host].append(ping_value if ping_value is not None else None)

        df = pd.concat([df, pd.DataFrame([{
            "timestamp": current_time,
            "host": host,
            "ping_ms": ping_value
        }])], ignore_index=True)

        # Trim history
        if len(history[host]) > MAX_POINTS:
            history[host] = history[host][-MAX_POINTS:]

    if len(timestamps) > MAX_POINTS:
        timestamps = timestamps[-MAX_POINTS:]

    # Update plot
    for host in HOSTS:
        lines[host].set_data(range(len(history[host])), history[host])

    ax.relim()
    ax.autoscale_view()
    return lines.values()

def save_log():
    df.to_csv(LOG_FILE, index=False)

ani = FuncAnimation(fig, update, interval=PING_INTERVAL * 1000)
try:
    plt.show()
except KeyboardInterrupt:
    print("Interrupted by user")
finally:
    save_log()
