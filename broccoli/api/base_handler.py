import os
import abc
from api.http_rpc_client import HttpRpcClient
from typing import Dict


class BaseHandler(metaclass=abc.ABCMeta):
    def __init__(self):
        self.http_rpc_client = HttpRpcClient(
            hostname=os.getenv("SERVER_HOSTNAME"),
            port=int(os.getenv("SERVER_PORT"))
        )

    @abc.abstractmethod
    def handle_request(self, path: str, query_params: Dict):
        pass
