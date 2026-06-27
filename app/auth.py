import functools

from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, redirect, url_for

from . import db


def hash_password(password):
    # CORRIGIDO: pbkdf2/scrypt com salt, no lugar de md5 sem salt.
    return generate_password_hash(password)


def register_user(name, email, password):
    db.query(
        "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
        (name, email, hash_password(password)),
        fetch=False,
    )


def authenticate(email, password):
    # CORRIGIDO: query parametrizada (sem SQLi) e verificação de hash em vez de
    # comparar strings de senha.
    rows = db.query(
        "SELECT id, name, email, password_hash FROM users WHERE email = %s",
        (email,),
    )
    if rows and check_password_hash(rows[0]["password_hash"], password):
        return {"id": rows[0]["id"], "name": rows[0]["name"], "email": rows[0]["email"]}
    return None


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("routes.login"))
        return view(*args, **kwargs)

    return wrapped


def current_user_id():
    return session.get("user_id")
