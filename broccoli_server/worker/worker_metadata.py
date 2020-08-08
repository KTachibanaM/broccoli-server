from typing import Dict
from dataclasses import dataclass


@dataclass
class WorkerMetadata:
    module_name: str
    args: Dict
    interval_seconds: int
    error_resiliency: int
