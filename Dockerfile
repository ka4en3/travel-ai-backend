# Dockerfile
FROM python:3.12-slim

# Set environment variable for production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installing system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

LABEL authors="k4n3"

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the whole backend app
COPY app ./app

COPY alembic.ini .
COPY alembic ./alembic
COPY entrypoint.sh /entrypoint.sh

EXPOSE 8000

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
