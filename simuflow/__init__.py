__version__ = '0.4.0'

import csv
import re
from scipy import interpolate
import numpy as np
from typing import List, Tuple


def read_inhalation_profile(fname: str, interval: int) -> Tuple[List[int], List[float]]:
  xdata = []
  ydata = []

  time_multiplicand = {
    's': 1000.0,
    'second': 1000.0,
    'seconds': 1000.0,
    'ms': 1.0,
    'millisecond': 1.0,
    'milliseconds': 1.0,
  }

  flow_multiplicand = {
    'L/m': 1.0,
    'L/min': 1.0,
    'L/s': 1/60,
    'L/second': 1/60,
  }

  with open(fname) as input_file:
    reader = csv.reader(input_file)
    time_mul = time_multiplicand['ms']
    flow_mul = flow_multiplicand['L/m']

    for idx, row in enumerate(reader):
      if idx == 0:
        time, flow = row
        m_time = re.search(r'time\((.*)\)', time)
        m_flow = re.search(r'flow\((.*)\)', flow)
        if m_time == None or m_flow == None:
          print('Time or flow now specified assuming ms and L/m')
        else:
          print(f'Using {time} and {flow}')
          time_mul = time_multiplicand[m_time[1]]
          flow_mul = flow_multiplicand[m_flow[1]]

        if time_mul == None or flow_mul == None:
          raise Exception(f'Error getting multiplicands, time: {time}, flow: {flow}')

      else:
        time, flow = row
        xdata.append(int(float(time)*time_mul))
        ydata.append(float(flow)*flow_mul)

  f = interpolate.interp1d(xdata, ydata)
  interp_x = np.arange(min(xdata), max(xdata), interval)
  interp_y = f(interp_x)
  print(f'Parsed data {len(interp_x)}, {len(interp_y)}')
  return (list(interp_x), list(interp_y))
