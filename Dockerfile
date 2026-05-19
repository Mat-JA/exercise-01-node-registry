# STAGE 1 - Builder
FROM python:3.14-slim AS builder

WORKDIR /app

# Instalar dependencias en un directorio local
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# STAGE 2 - Runtime
FROM python:3.14-slim

WORKDIR /app

# Crear usuario no-root PRIMERO
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Copiar dependencias al directorio del usuario appuser
COPY --from=builder --chown=appuser:appuser /install /usr/local

# Cambiar al usuario no-root
USER appuser

# Copiar código de la aplicación
COPY --chown=appuser:appuser . .

# Configuración
EXPOSE 8080

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health', timeout=2)" || exit 1

# Comando de inicio
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8080"]