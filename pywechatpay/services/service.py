from abc import ABCMeta

from ..core.client import Client


class ServiceABC(metaclass=ABCMeta):
    def __init__(self, client: Client):
        self.client = client
