from PySide6.QtWidgets import ( 
  QVBoxLayout, QFrame, QWidget, QPushButton, QLabel, QFileDialog,
)
from PySide6.QtCore import QSize, Qt, QDir, QObject

from simuflow.components.Graph import Canvas 
from simuflow.devices.simulator import simulator, Callback

class DisplayPanel(QFrame):
  def __init__(self, parent):
    super(DisplayPanel, self).__init__(parent)
    self.setObjectName('DisplayPanel')
    self.setStyleSheet("""
      #DisplayPanel { 
        margin:0px; 
        border:1px solid black; 
        min-width: 350px;
      }
    """)

    label = QLabel(self)
    label.setText('Output')
    label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
    
    self.layout = QVBoxLayout(self)

    graph = Canvas(self, 10000, 200)
    # graph.setFixedHeight(250)
    simulator.register(Callback.ON_FLOW_DATA, self.flow_callback)
    simulator.register(Callback.ON_SIMULATION_START, graph.clear_data)
    self.graph = graph

    # power = Canvas(self, 10000, 270, 2)
    # power.setFixedHeight(250)
    # self.power = power
    # simulator.register(Callback.ON_SIMULATION_START, power.clear_data)


    self.layout.addWidget(label)
    # self.layout.addWidget(power)
    self.layout.addWidget(graph)

    self.button = QPushButton("Export")
    self.button.clicked.connect(self.export)

    self.layout.addWidget(self.button)

  def flow_callback(self, data):
    # ts, flow, motor, driver = data
    ts, flow = data
    # self.power.update_data(ts, motor, driver)
    self.graph.update_data(ts, flow)

  def export(self):
    (file_name, _) = QFileDialog.getSaveFileName(caption="Save CSV")
    # TODO: better handling here
    if file_name == "": return
    print(file_name)

    if file_name.endswith(".csv") == False:
      file_name = f'{file_name}.csv'

    (xdata, ydata) = self.graph.get_data()
    with open(file_name, 'w') as f:
      f.write("time(ms),flow(l/min)\n")
      for (x, y) in zip(xdata, ydata):
        f.write(f'{x},{y}\n')