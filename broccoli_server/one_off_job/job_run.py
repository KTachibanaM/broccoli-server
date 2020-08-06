from dataclasses import dataclass
from typing import List, Dict


@dataclass
class JobRun:
    job_id: str
    state: str
    drained_log_lines: List[str]

    def to_json(self) -> Dict:
        return {
            "job_id": self.job_id,
            "state": self.state,
            "drained_log_lines": self.drained_log_lines
        }

    @staticmethod
    def from_json(d: Dict):
        return JobRun(
            d["job_id"],
            d["state"],
            d["drained_log_lines"]
        )
