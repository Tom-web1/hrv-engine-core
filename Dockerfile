# ---------- Base Python ----------
FROM python:3.11-slim

# ---------- Install system dependencies ----------
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libfreetype6-dev \
    libpng-dev \
    libjpeg-dev \
    libfontconfig1 \
    && apt-get clean

# ---------- Set work directory ----------
WORKDIR /app

# ---------- Copy project files ----------
COPY . /app

# ---------- Install Python dependencies ----------
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Ensure fonts are included ----------
# 將專案裡的 NotoSansTC 字型裝進系統，給 matplotlib 用
RUN mkdir -p /usr/share/fonts/truetype/noto
COPY fonts/*.ttf /usr/share/fonts/truetype/noto/
RUN fc-cache -f -v

# ---------- Expose Port ----------
EXPOSE 8080

# ---------- Start Gunicorn ----------
# Railway（或其他平台）通常會給一個環境變數 PORT
# 我們如果有拿到 PORT 就用它，沒有就用 8080
CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${PORT:-8080} app:app"]
