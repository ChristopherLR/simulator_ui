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
import csv
from pathlib import Path
from os import listdir
from os.path import isfile, join
from simuflow import read_inhalation_profile, __version__
from simuflow.packet import ConfigurationPacket
from simuflow.configuration import *

device = serial.Serial("/dev/tty.usbmodem1101", 115200)
interval = 2


peak = 80
duration = 4

kP = 150.0
kI = 0.15
kD = 0.0

exit_once_done = True
set_pid = True

hit_end = 0

global metadata
metadata = {"peak": peak, "duration": duration}


lin_x, lin_y = read_inhalation_profile(
    f"../inhalation_profiles/{peak}_{duration}.csv", interval
)

fig, ax = plt.subplots()
xdata, ydata = [], []
(ln,) = plt.plot([], [], "b", label="response")
plt.plot(lin_x, lin_y, label="input")
plt.legend()


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
        if msg[0] == "f":
            hit_start = 1
            [ts, flow] = msg[2:].split(",")
            # print(flow)
            update_data(x=int(ts), y=float(flow))
        elif msg[0] == "i" and msg != "interval":
            [pre_time, pre_flow] = msg.split(",")
            # print(pre_time[1:], pre_flow[2:])
            parsed_time = int(pre_time[1:])
            parsed_flow = float(pre_flow[2:])
            t_idx = lin_x.index(parsed_time)
            t_flow = lin_y[t_idx]
            if round(t_flow, 2) == parsed_flow:
                send_msg("ack")
            else:
                send_msg("nak")
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
    filename = f"measurements/dynamic_vacuum_l298n_sfm3000_{int(peak)}_{duration}.json"
    with open(filename, "a") as f:
        print(f"saving: {filename}")
        json.dump(
            {
                "sample_time": 1,
                "metadata": metadata,
                "time": xdata,
                "flow": ydata,
            },
            f,
        )
        f.write("\n")
    os.kill(os.getpid(), signal.SIGUSR1)
    if device.is_open:
        device.close()

    sys.exit(0)


def send_msg(msg):
    to_send = bytes(f"{msg}\r\n", "utf-8")
    print(f"send: {to_send}")
    device.write(to_send)
    time.sleep(0.003)


def send_json(msg):
    to_send = bytes(f"{json.dumps(msg)}\r\n", "utf-8")
    print(f"send: {to_send}")
    device.write(to_send)
    time.sleep(1)


def run():
    signal.signal(signal.SIGINT, exit_handler)
    x = threading.Thread(target=listen, daemon=True)
    x.start()

    send_json({"t": "connect", "version": __version__})

    if set_pid:
        send_json({"t": "pid", "kP": kP, "kI": kI, "kD": kD})

    packet = ConfigurationPacket()
    flow_config = DynamicFlow(
        lin_x, lin_y, len(lin_x), max(lin_x) - min(lin_x), interval
    )
    packet.flow_configuration = flow_config
    device.write(packet.toBytes())

    for x, y in zip(lin_x, lin_y):
        packet = ConfigurationPacket()
        packet.flow_configuration = DynamicFlowInterval(x, y)
        to_send = packet.toBytes()
        # print(f'send: {to_send}')
        device.write(to_send)
        time.sleep(0.003)

    packet = ConfigurationPacket()
    packet.flow_configuration = DynamicFlowInterval(max(lin_x) + interval, 0)
    packet.fin = 1
    to_send = packet.toBytes()
    print(f"send: {to_send}")
    device.write(to_send)
    time.sleep(1)

    # send_json({"t": "confirm"})

    send_json({"t": "run"})

    def init():
        # ax.set_xlim(0, 10000)
        # ax.set_ylim(0, 200)
        return (ln,)

    ani = FuncAnimation(fig, update, init_func=init, blit=True, interval=10)

    plt.show()


if __name__ == "__main__":
    run()
