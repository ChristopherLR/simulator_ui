from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt, QSize

class Canvas(FigureCanvasQTAgg):
  def __init__(self, parent=None, width=5, height=4, dpi=100):
    fig = Figure(figsize=(width, height), dpi=dpi)
    super(Canvas, self).__init__(fig)
    self.axes = fig.add_subplot(111)

class Graph(QFrame):
  def __init__(self, parent=None, width=300, height=300):
    super(Graph, self).__init__(parent)

    self.fig = Canvas(width=5, height=4, dpi=100)
    
    inner = QFrame(self)
    inner.layout = QVBoxLayout(inner)
    inner.layout.addWidget(self.fig)

    self.layout = QHBoxLayout(self)
    self.layout.addWidget(inner)