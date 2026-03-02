from typing import List

from letta_client import Letta

from letta.letta_agent import LettaAgent

class LettaMgr:
    client : Letta
    agent_id : str
    chat_id : str

    def __init__(self):
        key = "5gV7VJmBVw8LUwQr"
        host = "http://192.168.1.252:8283"
        self.client = Letta(base_url=host, api_key=key)
        self.agent_id = ""
        self.chat_id = ""