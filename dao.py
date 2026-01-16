import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("database.db")
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        cur = self.conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            cpf TEXT UNIQUE,
            password TEXT,
            is_admin INTEGER DEFAULT 0
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            code TEXT UNIQUE,
            value REAL
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS holdings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            stock_id INTEGER,
            quantity INTEGER,
            UNIQUE(user_id, stock_id)
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            stock_id INTEGER,
            quantity INTEGER,
            price REAL,
            type TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cur.execute("SELECT * FROM users WHERE is_admin=1")
        if cur.fetchone() is None:
            self.conn.execute(
                "INSERT INTO users (name, cpf, password, is_admin) VALUES (?,?,?,?)",
                ("Administrador", "00000000000", "admin123", 1)
            )
            self.conn.commit()
            print("Created standard ADM: CPF 00000000000 / Senha: admin123")

        self.conn.commit()

    def insert_user(self, name, cpf, password, is_admin):
        self.conn.execute(
            "INSERT INTO users(name, cpf, password, is_admin) VALUES (?,?,?,?)",
            (name, cpf, password, 1 if is_admin else 0)
        )
        self.conn.commit()

    def get_user_by_cpf(self, cpf):
        cur = self.conn.execute("SELECT * FROM users WHERE cpf=?", (cpf,))
        return cur.fetchone()

    def list_users(self):
        cur = self.conn.execute("SELECT * FROM users")
        return cur.fetchall()

    def update_user(self, uid, name, pw, is_admin):
        if is_admin is None:
            self.conn.execute("UPDATE users SET name=?, password=? WHERE id=?", (name, pw, uid))
        else:
            self.conn.execute("UPDATE users SET name=?, password=?, is_admin=? WHERE id=?", (name, pw, 1 if is_admin else 0, uid))
        self.conn.commit()

    def delete_user(self, uid):
        self.conn.execute("DELETE FROM users WHERE id=?", (uid,))
        self.conn.commit()

    def list_all_stocks(self):
        return self.conn.execute("SELECT * FROM stocks").fetchall()

    def insert_stock(self, name, code, value):
        self.conn.execute("INSERT INTO stocks(name, code, value) VALUES (?,?,?)", (name, code, value))
        self.conn.commit()

    def get_stock_by_code(self, code):
        return self.conn.execute("SELECT * FROM stocks WHERE code=?", (code,)).fetchone()

    def update_stock(self, sid, name, code, value):
        self.conn.execute("UPDATE stocks SET name=?, code=?, value=? WHERE id=?", (name, code, value, sid))
        self.conn.commit()

    def delete_stock(self, sid):
        self.conn.execute("DELETE FROM stocks WHERE id=?", (sid,))
        self.conn.commit()

    def upsert_holding(self, user_id, stock_id, qty):
        h = self.get_holding(user_id, stock_id)
        if h:
            new_qty = h["quantity"] + qty
            self.conn.execute("UPDATE holdings SET quantity=? WHERE id=?", (new_qty, h["id"]))
        else:
            self.conn.execute("INSERT INTO holdings(user_id, stock_id, quantity) VALUES (?,?,?)",
                              (user_id, stock_id, qty))
        self.conn.commit()

    def get_holding(self, user_id, stock_id):
        return self.conn.execute(
            "SELECT * FROM holdings WHERE user_id=? AND stock_id=?", (user_id, stock_id)
        ).fetchone()

    def list_user_holdings(self, user_id):
        return self.conn.execute("""
            SELECT h.quantity, s.name, s.code, s.value, s.id AS stock_id
            FROM holdings h
            JOIN stocks s ON h.stock_id = s.id
            WHERE h.user_id=?
        """, (user_id,)).fetchall()

    def add_transaction(self, user_id, stock_id, qty, price, tx_type):
        self.conn.execute(
            "INSERT INTO transactions(user_id, stock_id, quantity, price, type) VALUES (?,?,?,?,?)",
            (user_id, stock_id, qty, price, tx_type)
        )
        self.conn.commit()

    def list_transactions(self, user_id):
        return self.conn.execute("""
            SELECT t.*, s.code
            FROM transactions t
            JOIN stocks s ON t.stock_id = s.id
            WHERE t.user_id=?
            ORDER BY t.timestamp DESC
        """, (user_id,)).fetchall()
