import hashlib
import functools

from flask import session, redirect, url_for, request, flash

from . import db


def hash_password(password):
    # ACHADO (SAST/Bandit B324): md5 sem salt é hashing inseguro para senhas.
    # Correção futura: usar werkzeug.security.generate_password_hash / bcrypt.
    return hashlib.md5(password.encode()).hexdigest()


def register_user(name, email, password):
    db.query(
        "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
        (name, email, hash_password(password)),
        fetch=False,
    )


def authenticate(email, password):
    pw_hash = hash_password(password)
    # ACHADO (SAST/Bandit B608 + DAST SQLi): query construída por concatenação.
    sql = (
        "SELECT id, name, email FROM users "
        f"WHERE email = '{email}' AND password_hash = '{pw_hash}'"
    )
    rows = db.execute_raw(sql)
    return rows[0] if rows else None


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("routes.login"))
        return view(*args, **kwargs)

    return wrapped


def current_user_id():
    return session.get("user_id")
