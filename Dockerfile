FROM python:3.9-slim

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    tar \
    python3-tk \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    && rm -rf /var/lib/apt/lists/*

# Création du répertoire de travail
WORKDIR /app

# Copie des fichiers nécessaires
COPY installation.py .
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Configuration de l'affichage
ENV DISPLAY=host.docker.internal:0.0

# Commande par défaut
CMD ["python", "installation.py"]
