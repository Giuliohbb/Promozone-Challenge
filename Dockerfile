FROM python:3.12-slim

WORKDIR /app

# Instala dependências básicas
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala requisitos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o projeto
COPY . .

# Variáveis de ambiente para o Cloud Run
ENV PORT=8080
EXPOSE 8080

# Comando para rodar a API
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]