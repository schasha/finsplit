# FinSplit

Gestor de despesas compartilhadas (estilo Splitwise enxuto). Usuários criam
grupos, lançam despesas e o sistema calcula automaticamente os saldos e o acerto
mínimo de contas ("quem deve a quem").

Projeto desenvolvido como alvo de um pipeline DevSecOps (Secret Detection, SCA,
SAST, IaC Scanning e DAST).

## Stack

- **Backend/Web:** Python 3.10 + Flask (templates Jinja2 + endpoints JSON)
- **Banco de dados:** PostgreSQL 15 (acesso via psycopg2)
- **Infraestrutura:** Docker + docker-compose

## Arquitetura

```
Navegador ──HTTP──> Flask (gunicorn) ──SQL──> PostgreSQL
                       │
                       ├── app/auth.py       (cadastro, login, sessão)
                       ├── app/routes.py     (grupos, despesas, busca)
                       ├── app/balances.py   (cálculo de saldos e dívidas)
                       └── app/db.py         (conexão e queries)
```

## Como rodar

```bash
docker-compose up --build
# aplicação em http://localhost:5000
```

Primeiro acesso: crie uma conta em `/register`, faça login e crie um grupo.

## Estrutura

```
finsplit/
├── app/
│   ├── __init__.py      # app factory
│   ├── config.py        # configuração
│   ├── db.py            # conexão PostgreSQL
│   ├── auth.py          # autenticação
│   ├── routes.py        # rotas web/API
│   ├── balances.py      # lógica de negócio
│   └── templates/       # views Jinja2
├── schema.sql           # esquema do banco
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── .gitignore
```
