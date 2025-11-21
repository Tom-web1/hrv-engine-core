# ============================
# 1. Base Image
# ============================
FROM python:3.10-slim

# ============================
# 2. Install system deps
# ============================
RUN apt-get update && apt-get install -y \
    fontconfig \
    libfreetype6 \
    libpng16-16 \
    && rm -rf /var/lib/apt/lists/*

# ============================
# 3. Set workdir
# ============================
WORKDIR /app

# ============================
# 4. Copy project
# ============================
COPY . /app

# ============================
# 5. Install requirements
# ============================
RUN pip install --no-cache-dir -r requirements.txt

# ============================
# 6. Expose port
# ============================
ENV PORT=8080
EXPOSE 8080

# ============================
# 7. Start the app
# ============================
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
