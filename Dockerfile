# 使用輕量級 Python 3.9
FROM python:3.9-slim

# 設置工作目錄
WORKDIR /app

# 複製 requirements.txt 並安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製所有原始碼 (app.py, letta_manager.py)
COPY . .

# 暴露 Streamlit 預設端口
EXPOSE 8501

# 啟動指令，確保監聽所有 IP (0.0.0.0)
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]