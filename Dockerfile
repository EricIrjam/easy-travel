FROM python:3.11-slim

WORKDIR /app

# Copier tout le code backend
COPY . .

# Créer utilisateur non-root
RUN adduser --disabled-password appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Lancer votre main.py
CMD ["python", "main.py"]