from flask import (
    Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
)

from . import db
from . import auth
from .balances import group_net_balances, simplify_debts

bp = Blueprint("routes", __name__)


@bp.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("routes.login"))
    groups = db.query(
        "SELECT g.id, g.name FROM groups g "
        "JOIN group_members m ON m.group_id = g.id "
        "WHERE m.user_id = %s ORDER BY g.id DESC",
        (session["user_id"],),
    )
    return render_template("index.html", groups=groups)


# ---------------------------------------------------------------- auth
@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        auth.register_user(
            request.form["name"], request.form["email"], request.form["password"]
        )
        flash("Conta criada, faça login.")
        return redirect(url_for("routes.login"))
    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = auth.authenticate(request.form["email"], request.form["password"])
        if user:
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            return redirect(url_for("routes.index"))
        flash("Credenciais inválidas.")
    return render_template("login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("routes.login"))


# ---------------------------------------------------------------- groups
@bp.route("/groups", methods=["POST"])
@auth.login_required
def create_group():
    name = request.form["name"]
    rows = db.query(
        "INSERT INTO groups (name, owner_id) VALUES (%s, %s) RETURNING id",
        (name, auth.current_user_id()),
    )
    gid = rows[0]["id"]
    db.query(
        "INSERT INTO group_members (group_id, user_id) VALUES (%s, %s)",
        (gid, auth.current_user_id()),
        fetch=False,
    )
    return redirect(url_for("routes.view_group", group_id=gid))


@bp.route("/groups/<int:group_id>")
@auth.login_required
def view_group(group_id):
    group = db.query("SELECT id, name FROM groups WHERE id = %s", (group_id,))
    expenses = db.query(
        "SELECT e.id, e.description, e.amount, u.name AS payer "
        "FROM expenses e JOIN users u ON u.id = e.payer_id "
        "WHERE e.group_id = %s ORDER BY e.id DESC",
        (group_id,),
    )
    members = db.query(
        "SELECT u.id, u.name FROM users u "
        "JOIN group_members m ON m.user_id = u.id WHERE m.group_id = %s",
        (group_id,),
    )
    balances = group_net_balances(group_id)
    names = {m["id"]: m["name"] for m in members}
    transfers = [
        {"from": names.get(t["from"], t["from"]),
         "to": names.get(t["to"], t["to"]),
         "amount": t["amount"]}
        for t in simplify_debts(balances)
    ]
    return render_template(
        "group.html",
        group=group[0] if group else {"id": group_id, "name": "?"},
        expenses=expenses,
        members=members,
        transfers=transfers,
    )


@bp.route("/groups/<int:group_id>/expenses", methods=["POST"])
@auth.login_required
def add_expense(group_id):
    description = request.form["description"]
    amount = float(request.form["amount"])
    rows = db.query(
        "INSERT INTO expenses (group_id, payer_id, description, amount) "
        "VALUES (%s, %s, %s, %s) RETURNING id",
        (group_id, auth.current_user_id(), description, amount),
    )
    expense_id = rows[0]["id"]
    members = db.query(
        "SELECT user_id FROM group_members WHERE group_id = %s", (group_id,)
    )
    if members:
        share = round(amount / len(members), 2)
        for m in members:
            db.query(
                "INSERT INTO expense_shares (expense_id, user_id, share) "
                "VALUES (%s, %s, %s)",
                (expense_id, m["user_id"], share),
                fetch=False,
            )
    return redirect(url_for("routes.view_group", group_id=group_id))


# -------------------------------------------------- busca (CORRIGIDO: parametrizada)
@bp.route("/groups/<int:group_id>/search")
@auth.login_required
def search_expenses(group_id):
    term = request.args.get("q", "")
    # CORRIGIDO: o termo vai como parâmetro (%s), não concatenado. Sem SQLi.
    results = db.query(
        "SELECT id, description, amount FROM expenses "
        "WHERE group_id = %s AND description LIKE %s",
        (group_id, f"%{term}%"),
    )
    return render_template("search.html", results=results, term=term,
                           group_id=group_id)


# -------------------------------------------------- detalhe (CORRIGIDO: sem IDOR)
@bp.route("/expenses/<int:expense_id>")
@auth.login_required
def expense_detail(expense_id):
    # CORRIGIDO: só retorna a despesa se o usuário logado for membro do grupo
    # dela. O JOIN com group_members + filtro por user_id impede o IDOR.
    rows = db.query(
        "SELECT e.id, e.description, e.amount, e.group_id, u.name AS payer "
        "FROM expenses e "
        "JOIN users u ON u.id = e.payer_id "
        "JOIN group_members m ON m.group_id = e.group_id "
        "WHERE e.id = %s AND m.user_id = %s",
        (expense_id, auth.current_user_id()),
    )
    if not rows:
        return jsonify({"error": "not found"}), 404
    return jsonify(rows[0])
