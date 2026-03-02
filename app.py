# The `LettaAgent` class is a Python class that represents an agent with name and id attributes, and
# provides a static method to list agents from a client.
import time
import streamlit as st
import json
from typing import List
from functools import partial
from letta_client import Letta
from letta.letta_agent import LettaAgent
from letta.letta_chat import LettaChat
from letta.letta_mgr import LettaMgr
from letta.letta_msg import LettaMsg

# 1. 頁面基本配置
st.set_page_config(page_title="Letta 智能助手", layout="wide")

if "letta" not in st.session_state:
    st.session_state.letta = LettaMgr()

letta = st.session_state.letta


def process_chat_page(agent_id: str, chat_id: str):
    letta.chat_id = chat_id
    msgs = []
    if chat_id and chat_id not in ["new", "orig"]:
        st.write(f"正在顯示對話 ID: {chat_id}")
        msgs = LettaMsg.list(letta.client, agent_id, chat_id)
    elif chat_id == "orig":
        st.write("呢度係默認對話界面。")
        msgs = LettaMsg.list(letta.client, agent_id, chat_id)
    else:
        st.write("🆕 新對話已開啟")
    
    for msg in msgs:
        if msg.allow_dsp:
            with st.chat_message(msg.send_by):
                for cont in msg.dsp_cont:
                    if cont.type == "image":
                        st.image(cont.content, width = 150)
                    elif cont.type == "reasoning":
                        with st.expander("思考過程"):
                            st.write(cont.content)
                    elif cont.type == "code":
                        st.code(cont.content)
                    elif cont.type == "info":
                        st.info(cont.content)
                    elif cont.type == "success":
                        st.success(cont.content)
                    elif cont.type == "error":
                        st.error(cont.content)
                    elif cont.type == "warn":
                        st.warning(cont.content)
                    elif cont.type == "sys_alert":
                        with st.expander("思考過程"):
                            st.write(cont.content)
                    else:
                        st.markdown(cont.content)
                if msg.msg_type == "user_message":
                    st.caption("🧠 思考型" if msg.is_think_mode else "🚀 快捷")

    prompt = st.chat_input("請輸入提示詞", accept_file="multiple", accept_audio=True)


pages = []
chat_objects = []

# --- 側邊欄邏輯 ---
with st.sidebar:
    try:
        # 1. Agent 選擇
        agents = LettaAgent.list(letta.client)
        if agents:
            agent_map = {a.name: a.id for a in agents}
            selected_name = st.selectbox("Agent", list(agent_map.keys()))
            letta.agent_id = agent_map[selected_name]

        if letta.agent_id:
            # 建立「新對話」Page 物件
            new_chat_p = st.Page(
                partial(process_chat_page, agent_id=letta.agent_id, chat_id="new"),
                title="新對話",
                icon="➕",
                url_path="new",
            )
            pages.append(new_chat_p)

            # 建立「默認對話」Page 物件
            default_page = st.Page(
                partial(process_chat_page, agent_id=letta.agent_id, chat_id="orig"),
                title="默認對話",
                icon="💬",
                url_path="orig",
            )
            pages.append(default_page)

            # 獲取真實對話
            chats = LettaChat.list(letta.client, letta.agent_id)
            if chats:
                for chat in chats:
                    p = st.Page(
                        partial(
                            process_chat_page, agent_id=letta.agent_id, chat_id=chat.id
                        ),
                        title=chat.summary or "無標題對話",
                        icon="💬",
                        url_path=chat.id,
                    )
                    pages.append(p)
                    chat_objects.append(p)

    except Exception as e:
        st.error(f"連線異常: {e}")

# --- 執行導覽 ---
if pages:
    pg = st.navigation(pages, position="hidden")

    with st.sidebar:
        # 2. 開啟新對話掣
        if st.button("＋ 開啟新對話", use_container_width=True):
            st.switch_page(pages[0])

        # 3. 獲取當前路徑並處理斜槓問題
        # 用 .strip("/") 確保攞到嘅係 "new" 唔係 "/new"
        current_id = pg.url_path.strip("/") if pg.url_path else None

        # 判斷係咪真正可刪除嘅對話
        invalid_ids = ["orig", "new", ""]
        is_real_chat = current_id not in invalid_ids and current_id is not None

        if st.button(
            "🗑️ 刪除當前對話",
            use_container_width=True,
            type="primary",
            disabled=not is_real_chat,
        ):
            # 執行刪除 logic...
            st.rerun()

        st.divider()
        st.subheader("對話")

        # 4. 手動渲染清單
        st.page_link(pages[1], label="默認對話", icon="💬")

        for p in chat_objects:
            st.page_link(p, label=p.title, icon=p.icon)

    pg.run()
else:
    st.sidebar.info("請選擇 Agent")