FROM python:3.12-slim

# Evita .pyc e força stdout sem buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Instalar deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código
COPY src ./src
COPY .env .env

# Comando padrão: loop contínuo (pode sobrescrever no compose)
CMD ["python", "-m", "src.cli", "loop"]
