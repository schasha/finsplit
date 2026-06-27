from flask import Flask

from .config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = Config.SECRET_KEY

    # CORRIGIDO: endurecimento do cookie de sessão.
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    from .routes import bp
    app.register_blueprint(bp)

    # CORRIGIDO: cabeçalhos de segurança (resolve achados de headers ausentes do DAST).
    @app.after_request
    def set_security_headers(resp):
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Content-Security-Policy"] = "default-src 'self'"
        resp.headers["Referrer-Policy"] = "no-referrer"
        return resp

    return app
