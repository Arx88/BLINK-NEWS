FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "-u", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000", "--no-reload"]
