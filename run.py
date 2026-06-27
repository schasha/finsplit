import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    # CORRIGIDO: debug nunca é True por padrão; só liga via variável de ambiente
    # explícita em desenvolvimento. Em produção, servir via gunicorn.
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=5000, debug=debug)
