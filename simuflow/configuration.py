from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class SimulatorMetadata:
  simulator_version: str = 'unknown'
  ui_version: str = '0.2.0'

@dataclass
class FlowConfiguration(ABC):

  @abstractmethod
  def validate(self) -> bool:
    pass

@dataclass
class ConstantFlow(FlowConfiguration):
  flow: float = 0.0
  duration: int = 0

  def validate(self) -> bool:
    if self.duration <= 0: return False
    return True

@dataclass
class ManualFlow(FlowConfiguration):
  motor_state: int = 0
  driver: int = 0
  fan: int = 0

  def validate(self) -> bool:
    return True

@dataclass
class TriggerConfiguration():
  delay: int = 0