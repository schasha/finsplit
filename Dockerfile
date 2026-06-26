# ACHADO (IaC): imagem base sem pin por digest; idealmente usar SHA fixo.
FROM python:3.10

# ACHADO (IaC): roda como root (sem instrução USER) — Checkov CKV_DOCKER_3.
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# ACHADO (IaC): sem HEALTHCHECK — Checkov CKV_DOCKER_2.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
