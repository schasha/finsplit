# Remediação — FinSplit

Mapa de cada falha real encontrada pelo pipeline, o impacto e a correção aplicada.
Para o relatório, o "antes e depois" de cada item está disponível via `git diff`
entre o commit vulnerável e o commit de correção.

| # | Falha | Ferramenta | Impacto | Correção | Arquivo |
|---|-------|------------|---------|----------|---------|
| 1 | SQL Injection (login e busca) | SAST (Bandit B608/Semgrep) + DAST (ZAP) | Bypass de login e extração do banco | Queries parametrizadas (`%s`); remoção de `execute_raw` | `auth.py`, `routes.py`, `db.py` |
| 2 | Senha com MD5 sem salt | SAST (Bandit B324) | Quebra trivial de senhas se o banco vazar | `werkzeug.security` (pbkdf2/scrypt) + `check_password_hash` | `auth.py` |
| 3 | Segredos hardcoded | Secret (Gitleaks) + SAST | Forjar sessão e acessar o banco | Variáveis de ambiente obrigatórias, sem fallback | `config.py`, `docker-compose.yml` |
| 4 | `yaml.load` inseguro | SAST (Bandit B506) | RCE via YAML malicioso | `yaml.safe_load` | `config.py` |
| 5 | `debug=True` | SAST (Bandit B201) | RCE via console do Werkzeug | Debug desligado por padrão (via env) | `run.py` |
| 6 | XSS (refletido e armazenado) | DAST (ZAP) + SAST (Semgrep) | Roubo de sessão de outros usuários | Remoção de `\| safe`; autoescape do Jinja | `group.html`, `search.html` |
| 7 | IDOR / Broken Access Control | Análise manual a partir do DAST | Acesso a despesas de grupos alheios | Verificação de pertencimento ao grupo na query | `routes.py` |
| 8 | Container como root + sem HEALTHCHECK | IaC (Checkov CKV_DOCKER_3/2) | Privilégio root se a app for comprometida | `USER` não-root + `HEALTHCHECK` | `Dockerfile` |
| 9 | Senha padrão do Postgres + porta exposta | IaC (Checkov) | Banco acessível com credencial trivial | Segredo via `.env` + porta não publicada (`expose`) | `docker-compose.yml` |
| 10 | Dependências vulneráveis | SCA (Trivy) | Varia por CVE | Atualização para versões corrigidas | `requirements.txt` |
| 11 | Cabeçalhos de segurança ausentes | DAST (ZAP) | Clickjacking, MIME sniffing | Headers via `after_request` (CSP, X-CTO, X-Frame-Options) | `__init__.py` |

## Falsos positivos mantidos (documentados, não corrigidos)

- **Bandit B104 — bind em `0.0.0.0`**: intencional e necessário em container; a
  publicação para o host é controlada pelo compose. Não é exposição real.
- **Gitleaks no `.env.example`**: os campos são placeholders vazios/de exemplo.
- **ZAP "Suspicious Comments" / "Server version"** (low): sem segredo exposto;
  baixo impacto isolado.

## Próximos passos recomendados (reais, prioridade menor)

- Proteção CSRF nos formulários (ex.: Flask-WTF) — não implementado para manter
  o diff focado; documentado como melhoria.
- Pin da imagem base por digest SHA no Dockerfile.
