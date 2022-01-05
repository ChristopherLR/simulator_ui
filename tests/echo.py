import serial
import os
import signal
import sys
import time
import json
import threading


device = serial.Serial('/dev/tty.usbmodem111401', 115200)


def listen():
  while True:
    line = device.readline()
    msg = line.rstrip().decode('utf-8')
    print(msg)

def exit_handler(signum, frame):
  os.kill(os.getpid(), signal.SIGUSR1)
  if device.is_open:
    device.close()
  sys.exit(0)

def run():
  signal.signal(signal.SIGINT, exit_handler)
  x = threading.Thread(target=listen, daemon=True)
  x.start()

  while True:
    msg = { 'type': 'connect', 'version': '0.1.0' }
    to_send = bytes(f'{json.dumps(msg)}\r\n', 'utf-8')
    print(f'send: {to_send}')
    device.write(to_send)
    time.sleep(1)



if __name__ == '__main__':
    run()
