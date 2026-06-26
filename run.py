from app import create_app

app = create_app()

if __name__ == "__main__":
    # ACHADO (SAST/Bandit B201): debug=True expõe o debugger Werkzeug (RCE)
    # quando acessível. host 0.0.0.0 deixa a app exposta em todas as interfaces.
    app.run(host="0.0.0.0", port=5000, debug=True)
