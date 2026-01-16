from modelos import Admin, User, Investor
from dao import Database
import requests

db = Database()


def sign_up(is_admin=False):
    cpf = input("CPF (only numbers): ").replace(".", "").replace("-", "")
    if not cpf.isdigit() or len(cpf) != 11:
        print("Invalid CPF.")
        return
    if db.get_user_by_cpf(cpf):
        print("User already exists.")
        return
    name = input("Name: ")
    pw = input("Password: ")
    conf = input("Confirm password: ")
    if pw != conf:
        print("Passwords do not match.")
        return
    db.insert_user(name, cpf, pw, is_admin)
    print("User created successfully.")


def sign_in():
    cpf = input("CPF (only numbers): ").replace(".", "").replace("-", "")
    pw = input("Password: ")
    u = db.get_user_by_cpf(cpf)
    if not u or u["password"] != pw:
        print("Invalid credentials.")
        return None
    return Admin(u["name"], u["cpf"], u["password"]) if u["is_admin"] else User(u["name"], u["cpf"], u["password"])


def admin_login():
    print()
    print("--- ADMIN LOGIN ---")
    cpf = input("CPF: ").replace(".", "").replace("-", "")
    pw = input("Password: ")
    u = db.get_user_by_cpf(cpf)
    if not u or u["is_admin"] != 1:
        print("Not an admin or user not found.")
        return None
    if u["password"] != pw:
        print("Invalid password.")
        return None
    return Admin(u["name"], u["cpf"], u["password"])

#menus
def user_menu(user):
    while True:
        print()
        print(f"--- MENU ({user.role()}) ---")
        print("1 - Buy Stocks")
        print("2 - Sell Stocks")
        print("3 - Search Stocks")
        print("4 - Earnings")
        print("5 - Portfolio Valuation")
        print("6 - Transaction History")
        print("7 - Convert DOLLAR to REAL")
        print("0 - Back")
        op = input("Choose: ")

        if op == "1":
            buy_stock_for_user(user)
        elif op == "2":
            sell_stock_for_user(user)
        elif op == "3":
            search_stocks_system_and_user(user)
        elif op == "4":
            earnings_menu(user)
        elif op == "5":
            portfolio_valuation(user)
        elif op == "6":
            show_transactions(user)
        elif op == "7":
            conversion(user)
        elif op == "0":
            break
        else:
            print("Invalid option.")


def admin_menu(admin):
    while True:
        print()
        print(f"--- ADMIN MENU ({admin.name}) ---")
        print("1 - Manage Users")
        print("2 - Manage Stocks")
        print("0 - Back")
        op = input("Choose: ")

        if op == "1":
            crud_users()
        elif op == "2":
            crud_stocks()
        elif op == "0":
            break
        else:
            print("Invalid option.")


def main_loop():
    while True:
        print("\n--- HOME ---")
        print("1 - Sign Up (user)")
        print("2 - Sign In")
        print("3 - Admin Login")
        print("0 - Exit")
        op = input("Choose: ")

        if op == "0":
            print("Goodbye.")
            break
        elif op == "1":
            sign_up(is_admin=False)
        elif op == "2":
            user = sign_in()
            if user:
                if user.role() == "Administrator":
                    admin_menu(user)
                else:
                    user_menu(user)
        elif op == "3":
            admin = admin_login()
            if admin:
                admin_menu(admin)
        else:
            print("Invalid option.")

#crud usuarios
def crud_users():
    while True:
        print()
        print("--- USER CRUD ---")
        print("1 - List Users")
        print("2 - Add User")
        print("3 - Update User")
        print("4 - Delete User")
        print("0 - Back")
        op = input("Choose: ")

        if op == "1":
            users = db.list_users()
            for u in users:
                role = "ADMIN" if u["is_admin"] else "USER"
                print(f"{u['id']} - {u['name']} ({role}) CPF: {u['cpf']}")
        elif op == "2":
            sign_up(is_admin=input("Is admin? (y/n): ").lower() == "y")
        elif op == "3":
            try:
                uid_i = int(input("User ID to update: "))
            except:
                print("Invalid ID.")
                continue
            name = input("New name: ")
            pw = input("New password: ")
            if len(pw) <= 8:
                print('Your password is weak')

            adm = input("Make admin? (y/n/leave blank to keep): ").lower()
            if adm == "y":
                is_admin = True
            elif adm == "n":
                is_admin = False
            else:
                is_admin = None
            db.update_user(uid_i, name, pw, is_admin)
            print("User updated.")
        elif op == "4":
            try:
                uid_i = int(input("User ID to delete: "))
            except:
                print("Invalid ID.")
                continue
            confirm = input("Are you sure? type 'yes' to confirm: ")
            if confirm.lower() == "yes":
                db.delete_user(uid_i)
                print("User deleted.")
            else:
                print("Cancelled.")
        elif op == "0":
            break
        else:
            print("Invalid option.")

#crud stocks

def crud_stocks():
    while True:
        print()
        print("--- STOCK CRUD ---")
        print("1 - List Stocks")
        print("2 - Add Stock")
        print("3 - Update Stock")
        print("4 - Delete Stock")
        print("0 - Back")
        op = input("Choose: ")

        if op == "1":
            for s in db.list_all_stocks():
                print(f"{s['id']} - {s['name']} ({s['code']}) R$ {s['value']:.2f}")
        elif op == "2":
            name = input("Name: ")
            code = input("Code (ticker): ").upper()
            try:
                value = float(input("Value: "))
            except:
                print("Invalid value.")
                continue
            if db.get_stock_by_code(code):
                print("Stock code already exists.")
            else:
                db.insert_stock(name, code, value)
                print("Stock added.")
        elif op == "3":
            try:
                sid_i = int(input("Stock ID to update: "))

            except:
                print("Invalid ID.")
                continue
            name = input("New name: ")
            code = input("New code: ").upper()
            try:
                value = float(input("New value: "))
                if value <= 0:
                    print('You do not put negatives values')
                else:
                    db.update_stock(sid_i, name, code, value)
                    print("Stock updated.")
            except:
                print("Invalid value.")
                continue

        elif op == "4":
            try:
                sid_i = int(input("Stock ID to delete: "))
            except:
                print("Invalid ID.")
                continue
            confirm = input("Are you sure? type 'yes' to confirm: ")
            if confirm.lower() == "yes":
                db.delete_stock(sid_i)
                print("Stock deleted.")
            else:
                print("Cancelled.")
        elif op == "0":
            break
        else:
            print("Invalid option.")

#stocks
def buy_stock_for_user(user):
    print()
    print("--- stocks in system ---")
    for s in db.list_all_stocks():
        print(f"{s['name']} ({s['code']}) R$ {s['value']:.2f}")

    code = input("stock code: ").upper()
    try:
        qty = int(input("qty: "))
        price = float(input("price per unit paid: "))
    except:
        print("invalid input.")
        return
    stock = db.get_stock_by_code(code)
    if not stock:
        print("stock not found.")
        return
    u = db.get_user_by_cpf(user.cpf)
    db.upsert_holding(u["id"], stock["id"], qty)
    db.add_transaction(u["id"], stock["id"], qty, price, "BUY")
    print(f"Bought {qty} of {stock['name']} ({code}) at R$ {price:.2f}")


def sell_stock_for_user(user):
    code = input("stock to sell (code): ").upper()
    try:
        qty = int(input("qty to sell: "))
    except:
        print("invalid quantity.")
        return
    stock = db.get_stock_by_code(code)
    if not stock:
        print("stock not found.")
        return
    u = db.get_user_by_cpf(user.cpf)
    holding = db.get_holding(u["id"], stock["id"])
    if not holding or holding["quantity"] < qty:
        print("insufficient holdings.")
        return
    db.upsert_holding(u["id"], stock["id"], -qty)
    db.add_transaction(u["id"], stock["id"], qty, stock["value"], "SELL")
    print(f"Sold {qty} of {stock['name']} ({code}) at R$ {stock['value']:.2f}")


def search_stocks_system_and_user(user):
    print()
    print("--- stocks in system ---")
    for s in db.list_all_stocks():
        print(f"{s['name']} ({s['code']}) R$ {s['value']:.2f}")
    print()
    print("--- your holdings ---")
    u = db.get_user_by_cpf(user.cpf)
    holds = db.list_user_holdings(u["id"])
    if not holds:
        print("you have no holdings.")
        return
    for h in holds:
        total = h["quantity"] * h["value"]
        print(f"{h['name']} ({h['code']}) - {h['quantity']} x R$ {h['value']:.2f} = R$ {total:.2f}")

#outros requisitos

def earnings_menu(user):
    u = db.get_user_by_cpf(user.cpf)
    inv = Investor(db.list_user_holdings(u["id"]))
    while True:
        print()
        print("1 - dividends")
        print("2 - JCP")
        print("0 - back")
        op = input("choose: ")
        if op == "1":
            for name, value in inv.dividends():
                print(f"{name}: R$ {value:.2f}")
        elif op == "2":
            for name, value in inv.jcp():
                print(f"{name}: R$ {value:.2f}")
        elif op == "0":
            break
        else:
            print("invalid option.")


def portfolio_valuation(user):
    u = db.get_user_by_cpf(user.cpf)
    holds = db.list_user_holdings(u["id"])
    if not holds:
        print("no holdings.")
        return
    total = 0.0
    print()
    print("--- portfolio ---")
    for h in holds:
        val = h["quantity"] * h["value"]
        total += val
        print(f"{h['name']} ({h['code']}) - {h['quantity']} x R$ {h['value']:.2f} = R$ {val:.2f}")
    print(f"Total portfolio value: R$ {total:.2f}")


def show_transactions(user):
    u = db.get_user_by_cpf(user.cpf)
    txs = db.list_transactions(u["id"])
    if not txs:
        print("no transactions.")
        return
    print()
    print("--- transactions ---")
    for t in txs:
        print(f"[{t['timestamp']}] {t['type']} {t['quantity']} {t['code']} at R$ {t['price']:.2f}")

#api

def conversion(user):
    try:
        qty = int(input("type the quantity that you want to convert ($): "))
    except:
        print("invalid value.")
        return
    api = requests.get("https://economia.awesomeapi.com.br/last/USD-BRL")
    rate = float(api.json()["USDBRL"]["bid"])
    convert = qty * rate
    print(f"{convert:.2f} R$")
