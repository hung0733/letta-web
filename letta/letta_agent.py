
class LettaAgent:
    name : str = ""
    id : str = ""

    def __init__(self, agent):
        self.name = agent.name
        self.id = agent.id

    @staticmethod
    def list(client):
        agents = client.agents.list()
        return [LettaAgent(agent) for agent in (agents or [])]