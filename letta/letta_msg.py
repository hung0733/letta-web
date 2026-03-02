import json
from typing import List

class MsgCont:
    content : str
    type : str
    
    def __init__(self, content, type="text"):
        self.content = content
        self.type = type
        if self.type == "text":
            if len(self.content) > 0:
                if is_json(self.content):
                    self.type = "code" 

def is_json(my_str : str):
    try:
        json.loads(my_str)
    except ValueError:
        return False
    return True
    
def is_system_msg(content) -> bool:
    # 嘗試解析 JSON
    try:
        data = json.loads(content)
        # 如果符合你影張相入面嘅格式
        if data.get("type") == "system_alert":
            return True
    except:
        return False
    
    return False 

class LettaMsg:
    # 呢度只保留類型註解，唔好喺度初始化 List
    msg_type : str
    dsp_cont : List[MsgCont]
    is_think_mode : bool
    allow_dsp : bool
    send_by : str

    def __init__(self, msg):
        # 喺 __init__ 入面初始化，確保每個 instance 都有獨立嘅 List
        self.dsp_cont = []
        self.msg_type = msg.message_type
        content : str = getattr(msg, 'content', "")
        self.send_by = "assistant"
        self.is_think_mode = False
        self.allow_dsp = False

        if self.msg_type == "user_message":
            self.allow_dsp = True
            self.is_think_mode = True
            self.send_by = "user"
            
            if isinstance(content, list):
                for part in content:
                    partType = getattr(part, 'type', "")
                    if partType == "text":
                        text = getattr(part, 'text', "")
                        if text.startswith("/nothink"):
                            self.dsp_cont.append(MsgCont(text.replace("/nothink", "", 1).strip()))
                            self.is_think_mode = False
                        elif text.startswith("/think"):
                            self.dsp_cont.append(MsgCont(text.replace("/think", "", 1).strip()))  
                        else:
                            self.dsp_cont.append(MsgCont(text))
                    elif partType == "image":
                        imgSrc = getattr(part, 'source', None)
                        if imgSrc is not None:
                            imgType = imgSrc.type
                            if imgType == "base64":
                                self.dsp_cont.append(MsgCont(f"data:{imgSrc.media_type};base64,{imgSrc.data}", "image"))
                            elif imgType == "letta":
                                self.dsp_cont.append(MsgCont(f"data:{imgSrc.media_type};base64,{imgSrc.data}", "image"))
                            elif imgType == "url":
                                self.dsp_cont.append(MsgCont(imgSrc.url, "image"))
            elif isinstance(content, str): 
                if len(content) > 0:
                    if is_json(content):
                        if is_system_msg(content):
                            self.allow_dsp = False
                        else:
                            self.dsp_cont.append(MsgCont(content, "code"))
                    else:
                        if content.startswith("/nothink"):
                            self.dsp_cont.append(MsgCont(content.replace("/nothink", "", 1).strip()))
                            self.is_think_mode = False
                        elif content.startswith("/think"):
                            self.dsp_cont.append(MsgCont(content.replace("/think", "", 1).strip()))
                        else:
                            self.dsp_cont.append(MsgCont(content))
        elif self.msg_type == "assistant_message":
            self.dsp_cont.append(MsgCont(content))
            self.allow_dsp = True      
        elif self.msg_type == "reasoning_message":
            self.dsp_cont.append(MsgCont(msg.reasoning, "reasoning"))
            self.allow_dsp = True
        elif self.msg_type == "tool_call_message":
            # 修正：既然想顯示呼叫工具，就唔好隨即清空 self.dsp_cont = []
            self.dsp_cont.append(MsgCont(f"🛠️ 呼叫工具: [{msg.tool_call.name}]", "info"))
            self.allow_dsp = True
        elif self.msg_type == "tool_return_message":
            self.dsp_cont.append(MsgCont(f"✅ 工具回傳 (狀態: {msg.status})", "success"))
            self.dsp_cont.append(MsgCont(msg.tool_return, "code"))
            stderr = getattr(msg, 'stderr', [])
            if stderr and len(stderr) > 0:
                self.dsp_cont.append(MsgCont(' '.join(stderr), "error"))
            self.allow_dsp = True
        elif self.msg_type == "approval_request_message":
            self.dsp_cont.append(MsgCont(f"⚖️ 等待審批\n\n工具: {msg.tool_call.name}\n\nID: {msg.tool_call.tool_call_id}", "warn"))
            self.allow_dsp = True
        elif self.msg_type == "approval_response_message":
            self.dsp_cont.append(MsgCont(f"**審批結果**: {'✔️ 已批准' if msg.approve else '❌ 已拒絕'}\n\n**審批 ID**: {msg.approval_request_id}"))
            self.allow_dsp = True
        
    @staticmethod
    def list(client, agent_id : str, chat_id : str):
        msgs = []
        if chat_id == "orig":
            msgs = client.agents.messages.list(agent_id = agent_id)
        else:
            msgs = client.conversations.messages.list(conversation_id = chat_id)
        
        return [LettaMsg(msg) for msg in (msgs or [])]