from ePIC_benchmarks.parsl._base import BaseParslModel
from typing import Optional, Any, Literal, Type, ClassVar
from parsl.monitoring.monitoring import MonitoringHub

class ParslMonitoringHub(BaseParslModel):

    config_type_name : Literal['MonitoringHub'] = 'MonitoringHub'
    config_type : ClassVar[Type] = MonitoringHub

    hub_address: str
    hub_port: Optional[int] = None
    hub_port_range: Any = None

    workflow_name: Optional[str] = None
    workflow_version: Optional[str] = None
    logging_endpoint: Optional[str] = None
    monitoring_debug: bool = False
    resource_monitoring_enabled: bool = True
    resource_monitoring_interval: float = 30