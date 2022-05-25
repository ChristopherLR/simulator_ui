import serial
import os
import signal
import sys
import time
import json
import threading
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

device = serial.Serial("/dev/tty.usbmodem1101", 115200)

setpoint = 100.0
duration = 5000


kP = 150.0
kI = 0.15
kD = 0.0

set_pid = True
exit_once_done = True
save_once_done = True

hit_end = 0

global metadata
metadata = {"setpoint": setpoint, "duration": duration}

fig, ax = plt.subplots()
xdata, ydata = [], []
(ln,) = plt.plot([], [], "b")


def update_data(x, y):
    xdata.append(x)
    ydata.append(y)
    # ln.set_data(xdata, ydata)
    # return ln,


def update(frame):
    ln.set_data(xdata, ydata)
    return (ln,)


def listen():
    hit_start = 0
    while True:
        line = device.readline()
        msg = line.rstrip().decode("utf-8")
        # print(msg)
        if msg[0] == "f":
            [ts, flow] = msg[2:].split(",")
            if hit_start == 0 and float(flow) >= setpoint:
                hit_start = ts
                print(ts)
            # print(flow)
            update_data(x=int(ts), y=float(flow))
        elif msg == "alive":
            print("X", end="")
            if hit_start != 0 and exit_once_done:
                exit_handler(None, None)
        else:
            print(msg)
            global metadata
            try:
                data = json.loads(msg)
                metadata |= data
            except Exception:
                pass


def exit_handler(signum, frame):
    filename = (
        f"measurements/const_vacuum_l298n_sfm3000_{int(setpoint)}_{duration}.json"
    )
    if save_once_done:
        with open(filename, "a") as f:
            print(f"saving: {filename}")
            json.dump(
                {
                    "metadata": metadata,
                    "time": xdata,
                    "flow": ydata,
                    "sample_time": 1,
                },
                f,
            )
            f.write("\n")
    os.kill(os.getpid(), signal.SIGUSR1)
    if device.is_open:
        device.close()

    sys.exit(0)


def send_msg(msg):
    to_send = bytes(f"{json.dumps(msg)}\r\n", "utf-8")
    print(f"send: {to_send}")
    device.write(to_send)
    time.sleep(1)


def run():
    signal.signal(signal.SIGINT, exit_handler)
    x = threading.Thread(target=listen, daemon=True)
    x.start()

    send_msg({"t": "connect", "version": "0.1.0"})

    if set_pid:
        send_msg({"t": "pid", "kP": kP, "kI": kI, "kD": kD})

    send_msg({"t": "const", "dl": 0, "f": int(setpoint), "d": duration})

    def init():
        ax.set_xlim(0, duration + duration * 0.5)
        ax.set_ylim(0, setpoint + setpoint * 0.5)
        return (ln,)

    ani = FuncAnimation(fig, update, init_func=init, blit=True, interval=5)

    plt.show()


if __name__ == "__main__":
    run()
