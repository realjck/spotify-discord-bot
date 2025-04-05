# Utilise une image Python alpine minimale
FROM python:3.10-alpine

# Désactive le buffering de Python pour les logs en temps réel
ENV PYTHONUNBUFFERED=1

# Crée et définit le répertoire de travail
WORKDIR /app

# Copie uniquement les fichiers nécessaires
COPY spotify-bot.py requirements.txt ./

# Installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Variable d'environnement pour le token (à passer au run)
ENV DISCORD_TOKEN=""
ENV SPOTIFY_CLIENT_ID=""
ENV SPOTIFY_CLIENT_SECRET=""

# Lance le bot
CMD ["python", "spotify-bot.py"]