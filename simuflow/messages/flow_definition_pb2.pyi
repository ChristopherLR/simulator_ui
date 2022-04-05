"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import google.protobuf.descriptor
import google.protobuf.internal.enum_type_wrapper
import google.protobuf.message
import typing
import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

class InterfaceMessage(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    class _MessageType:
        ValueType = typing.NewType('ValueType', builtins.int)
        V: typing_extensions.TypeAlias = ValueType
    class _MessageTypeEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[InterfaceMessage._MessageType.ValueType], builtins.type):
        DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
        kVersionInfo: InterfaceMessage._MessageType.ValueType  # 0
        kConstantFlow: InterfaceMessage._MessageType.ValueType  # 1
        kManualFlow: InterfaceMessage._MessageType.ValueType  # 2
        kDynamicFlow: InterfaceMessage._MessageType.ValueType  # 3
        kDynamicFlowInterval: InterfaceMessage._MessageType.ValueType  # 4
        kInformationRequest: InterfaceMessage._MessageType.ValueType  # 5
    class MessageType(_MessageType, metaclass=_MessageTypeEnumTypeWrapper):
        pass

    kVersionInfo: InterfaceMessage.MessageType.ValueType  # 0
    kConstantFlow: InterfaceMessage.MessageType.ValueType  # 1
    kManualFlow: InterfaceMessage.MessageType.ValueType  # 2
    kDynamicFlow: InterfaceMessage.MessageType.ValueType  # 3
    kDynamicFlowInterval: InterfaceMessage.MessageType.ValueType  # 4
    kInformationRequest: InterfaceMessage.MessageType.ValueType  # 5

    MESSAGE_TYPE_FIELD_NUMBER: builtins.int
    VERSION_INFO_FIELD_NUMBER: builtins.int
    CONSTANT_FLOW_FIELD_NUMBER: builtins.int
    DYNAMIC_FLOW_FIELD_NUMBER: builtins.int
    MANUAL_FLOW_FIELD_NUMBER: builtins.int
    DYNAMIC_FLOW_INTERVAL_FIELD_NUMBER: builtins.int
    INFORMATION_REQUEST_FIELD_NUMBER: builtins.int
    message_type: global___InterfaceMessage.MessageType.ValueType
    @property
    def version_info(self) -> global___VersionInfo: ...
    @property
    def constant_flow(self) -> global___ConstantFlow: ...
    @property
    def dynamic_flow(self) -> global___DynamicFlow: ...
    @property
    def manual_flow(self) -> global___ManualFlow: ...
    @property
    def dynamic_flow_interval(self) -> global___DynamicFlowInterval: ...
    @property
    def information_request(self) -> global___InformationRequest: ...
    def __init__(self,
        *,
        message_type: global___InterfaceMessage.MessageType.ValueType = ...,
        version_info: typing.Optional[global___VersionInfo] = ...,
        constant_flow: typing.Optional[global___ConstantFlow] = ...,
        dynamic_flow: typing.Optional[global___DynamicFlow] = ...,
        manual_flow: typing.Optional[global___ManualFlow] = ...,
        dynamic_flow_interval: typing.Optional[global___DynamicFlowInterval] = ...,
        information_request: typing.Optional[global___InformationRequest] = ...,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["constant_flow",b"constant_flow","dynamic_flow",b"dynamic_flow","dynamic_flow_interval",b"dynamic_flow_interval","information_request",b"information_request","manual_flow",b"manual_flow","message",b"message","version_info",b"version_info"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["constant_flow",b"constant_flow","dynamic_flow",b"dynamic_flow","dynamic_flow_interval",b"dynamic_flow_interval","information_request",b"information_request","manual_flow",b"manual_flow","message",b"message","message_type",b"message_type","version_info",b"version_info"]) -> None: ...
    def WhichOneof(self, oneof_group: typing_extensions.Literal["message",b"message"]) -> typing.Optional[typing_extensions.Literal["version_info","constant_flow","dynamic_flow","manual_flow","dynamic_flow_interval","information_request"]]: ...
global___InterfaceMessage = InterfaceMessage

class SimulatorMessage(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    class _MessageType:
        ValueType = typing.NewType('ValueType', builtins.int)
        V: typing_extensions.TypeAlias = ValueType
    class _MessageTypeEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[SimulatorMessage._MessageType.ValueType], builtins.type):
        DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
        kVersionInfo: SimulatorMessage._MessageType.ValueType  # 0
        kFlow: SimulatorMessage._MessageType.ValueType  # 1
    class MessageType(_MessageType, metaclass=_MessageTypeEnumTypeWrapper):
        pass

    kVersionInfo: SimulatorMessage.MessageType.ValueType  # 0
    kFlow: SimulatorMessage.MessageType.ValueType  # 1

    MESSAGE_TYPE_FIELD_NUMBER: builtins.int
    VERSION_INFO_FIELD_NUMBER: builtins.int
    FLOW_INFO_FIELD_NUMBER: builtins.int
    message_type: global___SimulatorMessage.MessageType.ValueType
    @property
    def version_info(self) -> global___VersionInfo: ...
    @property
    def flow_info(self) -> global___FlowInfo: ...
    def __init__(self,
        *,
        message_type: global___SimulatorMessage.MessageType.ValueType = ...,
        version_info: typing.Optional[global___VersionInfo] = ...,
        flow_info: typing.Optional[global___FlowInfo] = ...,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["flow_info",b"flow_info","message",b"message","version_info",b"version_info"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["flow_info",b"flow_info","message",b"message","message_type",b"message_type","version_info",b"version_info"]) -> None: ...
    def WhichOneof(self, oneof_group: typing_extensions.Literal["message",b"message"]) -> typing.Optional[typing_extensions.Literal["version_info","flow_info"]]: ...
global___SimulatorMessage = SimulatorMessage

class FlowInfo(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    FLOW_FIELD_NUMBER: builtins.int
    TIMESTAMP_FIELD_NUMBER: builtins.int
    flow: builtins.float
    timestamp: builtins.int
    def __init__(self,
        *,
        flow: builtins.float = ...,
        timestamp: builtins.int = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["flow",b"flow","timestamp",b"timestamp"]) -> None: ...
global___FlowInfo = FlowInfo

class ConstantFlow(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    FLOW_FIELD_NUMBER: builtins.int
    DURATION_FIELD_NUMBER: builtins.int
    flow: builtins.float
    duration: builtins.int
    def __init__(self,
        *,
        flow: builtins.float = ...,
        duration: builtins.int = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["duration",b"duration","flow",b"flow"]) -> None: ...
global___ConstantFlow = ConstantFlow

class ManualFlow(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    class _FanDirection:
        ValueType = typing.NewType('ValueType', builtins.int)
        V: typing_extensions.TypeAlias = ValueType
    class _FanDirectionEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[ManualFlow._FanDirection.ValueType], builtins.type):
        DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
        kClockwise: ManualFlow._FanDirection.ValueType  # 0
        kCounterClockwise: ManualFlow._FanDirection.ValueType  # 1
    class FanDirection(_FanDirection, metaclass=_FanDirectionEnumTypeWrapper):
        pass

    kClockwise: ManualFlow.FanDirection.ValueType  # 0
    kCounterClockwise: ManualFlow.FanDirection.ValueType  # 1

    FLOW_FIELD_NUMBER: builtins.int
    DRIVER_FIELD_NUMBER: builtins.int
    FAN_DIRECTION_FIELD_NUMBER: builtins.int
    flow: builtins.float
    driver: builtins.int
    fan_direction: global___ManualFlow.FanDirection.ValueType
    def __init__(self,
        *,
        flow: builtins.float = ...,
        driver: builtins.int = ...,
        fan_direction: global___ManualFlow.FanDirection.ValueType = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["driver",b"driver","fan_direction",b"fan_direction","flow",b"flow"]) -> None: ...
global___ManualFlow = ManualFlow

class DynamicFlow(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    DURATION_FIELD_NUMBER: builtins.int
    COUNT_FIELD_NUMBER: builtins.int
    INTERVAL_FIELD_NUMBER: builtins.int
    duration: builtins.int
    count: builtins.int
    interval: builtins.int
    def __init__(self,
        *,
        duration: builtins.int = ...,
        count: builtins.int = ...,
        interval: builtins.int = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["count",b"count","duration",b"duration","interval",b"interval"]) -> None: ...
global___DynamicFlow = DynamicFlow

class DynamicFlowInterval(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    INTERVAL_FIELD_NUMBER: builtins.int
    FLOW_FIELD_NUMBER: builtins.int
    FINAL_FIELD_NUMBER: builtins.int
    interval: builtins.int
    flow: builtins.float
    final: builtins.int
    def __init__(self,
        *,
        interval: builtins.int = ...,
        flow: builtins.float = ...,
        final: builtins.int = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["final",b"final","flow",b"flow","interval",b"interval"]) -> None: ...
global___DynamicFlowInterval = DynamicFlowInterval

class InformationRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    class _DataType:
        ValueType = typing.NewType('ValueType', builtins.int)
        V: typing_extensions.TypeAlias = ValueType
    class _DataTypeEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[InformationRequest._DataType.ValueType], builtins.type):
        DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
        kDynamicFlow: InformationRequest._DataType.ValueType  # 0
    class DataType(_DataType, metaclass=_DataTypeEnumTypeWrapper):
        pass

    kDynamicFlow: InformationRequest.DataType.ValueType  # 0

    DATA_TYPE_FIELD_NUMBER: builtins.int
    data_type: global___InformationRequest.DataType.ValueType
    def __init__(self,
        *,
        data_type: global___InformationRequest.DataType.ValueType = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["data_type",b"data_type"]) -> None: ...
global___InformationRequest = InformationRequest

class VersionInfo(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    MAJOR_FIELD_NUMBER: builtins.int
    MINOR_FIELD_NUMBER: builtins.int
    PATCH_FIELD_NUMBER: builtins.int
    major: builtins.int
    minor: builtins.int
    patch: builtins.int
    def __init__(self,
        *,
        major: builtins.int = ...,
        minor: builtins.int = ...,
        patch: builtins.int = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["major",b"major","minor",b"minor","patch",b"patch"]) -> None: ...
global___VersionInfo = VersionInfo