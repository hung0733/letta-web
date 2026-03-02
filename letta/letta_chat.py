
class LettaChat:
    id : str = ""
    summary : str = ""

    def __init__(self, chat):
        self.summary = chat.summary
        self.id = chat.id

    @staticmethod
    def list(client, agent_id):
        chats = client.conversations.list(agent_id = agent_id)
        return [LettaChat(chat) for chat in (chats or [])]