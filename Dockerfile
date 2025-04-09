FROM python:3.12-slim

# Installing system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

LABEL authors="k4n3"

WORKDIR /app

COPY backend/requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY app ./app
COPY backend/alembic ./alembic
COPY backend/alembic.ini .

EXPOSE 8000

CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
