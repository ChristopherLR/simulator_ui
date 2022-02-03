
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure
from random import random 

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt, QSize

class Canvas(QFrame):
  def __init__(self, parent, xlim, ylim, plot_count = 1):
    super(Canvas, self).__init__(parent)
    dynamic_canvas = FigureCanvasQTAgg(Figure(figsize=(10, 8)))
    self.layout = QVBoxLayout(self)

    self.xdata = []
    self.plot_count = plot_count
    self.create_data_map()


    self.axes = dynamic_canvas.figure.subplots()
    self.axes.set_xlim(0, xlim)
    self.axes.set_xlabel('Time(ms)')
    self.axes.set_ylim(0, ylim)
    self.axes.set_ylabel('Flow(L/m)')
    color_map = ['b', 'g', 'r', 'c', 'y']

    self.lines = []
    for i in range(self.plot_count):
      ln, = self.axes.plot([], [], color_map[i])
      self.lines.append(ln)

    self.timer = dynamic_canvas.new_timer(50)
    self.timer.add_callback(self.update_canvas)
    self.timer.start()

    self.layout.addWidget(dynamic_canvas)
  
  def create_data_map(self):
    self.ydata_map = []
    for i in range(self.plot_count):
      self.ydata_map.append([])

  def update_data(self, x, *y):
    self.xdata.append(x)
    for idx, ydata in enumerate(y):
      self.ydata_map[idx].append(ydata)

  def update_canvas(self):
    for i in range(self.plot_count):
      self.lines[i].set_data(self.xdata, self.ydata_map[i])
    self.lines[0].figure.canvas.draw()

  def clear_data(self, res):
    self.xdata.clear()
    self.ydata_map.clear()
    # print(self.ydata_map)
    self.create_data_map()
    # print(self.ydata_map)
    for i in range(self.plot_count):
      self.lines[i].set_data(self.xdata, self.ydata_map[i])
      self.lines[i].figure.canvas.draw()

  def get_data(self):
    return (self.xdata, self.ydata_map[0])

class MultiCanvas(QFrame):
  def __init__(self, parent, xlim, ylim, plot_config):
    super(MultiCanvas, self).__init__(parent)
    dynamic_canvas = FigureCanvasQTAgg(Figure(figsize=(5, 4)))
    toolbar = NavigationToolbar(dynamic_canvas, self)

    self.xdata = []
    self.plot_config = { }
    self.plot_count = len(plot_config)


    self.axes = dynamic_canvas.figure.subplots()
    self.axes.set_xlim(0, xlim)
    self.axes.set_ylim(0, ylim)
    color_map = ['b', 'g', 'r', 'c', 'y']


    for idx, pc in enumerate(plot_config):
      ln, = self.axes.plot([], [], color_map[idx])
      self.plot_config[pc['name']] = {
        'line': ln,
        'xdata': [],
        'ydata': [],
      }

    self.timer = dynamic_canvas.new_timer(50)
    self.timer.add_callback(self.update_canvas)
    self.timer.start()

    self.layout = QVBoxLayout(self)
    self.layout.addWidget(dynamic_canvas)
    self.layout.addWidget(toolbar)
    print(self.plot_config)

  def update_plot_bounds(self, xlim, ylim):
    self.axes.set_xlim(0, xlim)
    self.axes.set_ylim(0, ylim)

  def update_data(self, name, x, y):
    self.plot_config[name]['xdata'].append(x)
    self.plot_config[name]['ydata'].append(y)

  def update_plot(self, name, xdata, ydata):
    print('Update plot')
    self.plot_config[name]['xdata'] = xdata
    self.plot_config[name]['ydata'] = ydata
    self.update_canvas()

  def update_canvas(self):
    for k in self.plot_config.keys():
      plot = self.plot_config[k]
      plot['line'].set_data(plot['xdata'], plot['ydata'])
      plot['line'].figure.canvas.draw()

  def clear_data(self, name, res):
    plot = self.plot_config[name]
    plot['xdata'].clear()
    plot['ydata'].clear()
    plot['line'].set_data(plot['xdata'], plot['ydata'])
    plot['line'].figure.canvas.draw()

class Graph(QFrame):
  def __init__(self, parent=None, width=300, height=300):
    super(Graph, self).__init__(parent)

    self.fig = Canvas(width=10, height=8, dpi=100)
    
    inner = QFrame(self)
    inner.layout = QVBoxLayout(inner)
    inner.layout.addWidget(self.fig)

    self.layout = QHBoxLayout(self)
    self.layout.addWidget(inner)