FROM python:3.11-alpine

WORKDIR /app

# Установка зависимостей системы
RUN apk update && rm -rf /var/cache/apk/*

# RUN rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8000

CMD ["python", "main.py"]