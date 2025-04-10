# Dockerfile
FROM python:3.12-slim

LABEL authors="k4n3"

# Set environment variable for production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY app ./

RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
