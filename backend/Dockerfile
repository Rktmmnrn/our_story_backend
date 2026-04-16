FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances système si nécessaire (ex: libpq pour postgres)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Création de l'arborescence média
RUN mkdir -p /app/media/photos /app/media/videos /app/media/music

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]