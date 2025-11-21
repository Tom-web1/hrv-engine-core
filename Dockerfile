# 使用 Debian slim 版 Python 映像
FROM python:3.12-slim

# 工作目錄
WORKDIR /app

# 安裝必要系統套件（不再裝 ttf-mscorefonts-installer）
RUN apt-get update && apt-get install -y \
    build-essential \
    fontconfig \
  && rm -rf /var/lib/apt/lists/*

# 先安裝 Python 套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案程式碼
COPY . .

# headless 繪圖用
ENV MPLBACKEND=Agg
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# 對外開放的 port
EXPOSE 8000

# 啟動 Flask app（app.py 裡的 app 物件）
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
