FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# CORRIGIDO: cria e usa um usuário não-root (Checkov CKV_DOCKER_3).
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

EXPOSE 5000

# CORRIGIDO: HEALTHCHECK definido (Checkov CKV_DOCKER_2).
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/login')" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
