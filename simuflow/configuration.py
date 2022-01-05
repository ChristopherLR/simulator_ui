from dataclasses import dataclass
from abc import ABC, abstractmethod
from simuflow.devices.simulator import Callback

@dataclass
class SimulatorMetadata:
  cb: Callback = Callback.ON_METADATA_UPDATE
  simulator_version: str = 'unknown'
  ui_version: str = '0.1.0'

@dataclass
class FlowConfiguration(ABC):
  cb: Callback

  @abstractmethod
  def validate(self) -> bool:
    pass

@dataclass
class ConstantFlow(FlowConfiguration):
  cb: Callback = Callback.ON_CONST_FLOW_UPDATE
  flow: float = 0.0
  duration: int = 0

  def validate(self) -> bool:
    if self.duration <= 0: return False
    return True

@dataclass
class ManualFlow(FlowConfiguration):
  cb: Callback = Callback.ON_MANUAL_FLOW_UPDATE
  motor_state: int = 0
  driver: int = 0
  fan: int = 0

  def validate(self) -> bool:
    return True

@dataclass
class TriggerConfiguration():
  cb: Callback = Callback.ON_TRIGGER_UPDATE
  delay: int = 0