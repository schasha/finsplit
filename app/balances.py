"""Lógica de negócio do FinSplit: a partir das despesas e cotas de um grupo,
calcula o saldo líquido de cada membro e simplifica em 'quem deve a quem'."""

from . import db


def group_net_balances(group_id):
    """Retorna {user_id: saldo}. Positivo = tem a receber; negativo = deve."""
    paid = db.query(
        "SELECT payer_id AS uid, COALESCE(SUM(amount),0) AS total "
        "FROM expenses WHERE group_id = %s GROUP BY payer_id",
        (group_id,),
    )
    owed = db.query(
        "SELECT s.user_id AS uid, COALESCE(SUM(s.share),0) AS total "
        "FROM expense_shares s "
        "JOIN expenses e ON e.id = s.expense_id "
        "WHERE e.group_id = %s GROUP BY s.user_id",
        (group_id,),
    )

    balances = {}
    for row in paid:
        balances[row["uid"]] = balances.get(row["uid"], 0) + float(row["total"])
    for row in owed:
        balances[row["uid"]] = balances.get(row["uid"], 0) - float(row["total"])

    return {uid: round(bal, 2) for uid, bal in balances.items()}


def simplify_debts(balances):
    """Transforma os saldos líquidos numa lista mínima de transferências."""
    creditors = sorted(
        [[uid, bal] for uid, bal in balances.items() if bal > 0],
        key=lambda x: -x[1],
    )
    debtors = sorted(
        [[uid, -bal] for uid, bal in balances.items() if bal < 0],
        key=lambda x: -x[1],
    )

    transfers = []
    i = j = 0
    while i < len(debtors) and j < len(creditors):
        debtor, owes = debtors[i]
        creditor, due = creditors[j]
        amount = round(min(owes, due), 2)
        if amount > 0:
            transfers.append({"from": debtor, "to": creditor, "amount": amount})
        debtors[i][1] -= amount
        creditors[j][1] -= amount
        if debtors[i][1] <= 0.009:
            i += 1
        if creditors[j][1] <= 0.009:
            j += 1
    return transfers
