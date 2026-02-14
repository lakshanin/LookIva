import sqlite3
import os
from datetime import datetime, date

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lookiva.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            batch_id TEXT PRIMARY KEY,
            base_product_id TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'Saree',
            product_name TEXT NOT NULL,
            fabric TEXT,
            color TEXT,
            pattern TEXT,
            size TEXT,
            source TEXT,
            cost_per_unit REAL NOT NULL DEFAULT 0,
            first_purchase_date DATE,
            image_path TEXT,
            remarks TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            batch_id TEXT NOT NULL,
            supplier_name TEXT,
            quantity INTEGER NOT NULL DEFAULT 0,
            cost_per_unit REAL NOT NULL DEFAULT 0,
            payment_method TEXT DEFAULT 'Cash',
            remarks TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (batch_id) REFERENCES products(batch_id)
        );

        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            batch_id TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            selling_price_customer REAL NOT NULL DEFAULT 0,
            selling_price_retailer REAL NOT NULL DEFAULT 0,
            sale_type TEXT NOT NULL DEFAULT 'Direct',
            remarks TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (batch_id) REFERENCES products(batch_id)
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            expense_type TEXT NOT NULL,
            description TEXT,
            amount REAL NOT NULL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS cash_flow (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            description TEXT,
            inflow REAL DEFAULT 0,
            outflow REAL DEFAULT 0,
            pending_type TEXT,
            status TEXT DEFAULT 'Completed',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS capital (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            description TEXT,
            type TEXT NOT NULL,
            amount REAL NOT NULL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()


# --------------- Products ---------------

def add_product(batch_id, base_product_id, category, product_name, fabric=None,
                color=None, pattern=None, size=None, source=None,
                cost_per_unit=0, first_purchase_date=None, image_path=None, remarks=None):
    conn = get_connection()
    conn.execute(
        """INSERT INTO products (batch_id, base_product_id, category, product_name,
           fabric, color, pattern, size, source, cost_per_unit, first_purchase_date,
           image_path, remarks)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (batch_id, base_product_id, category, product_name, fabric, color,
         pattern, size, source, cost_per_unit, first_purchase_date, image_path, remarks)
    )
    conn.commit()
    conn.close()


def get_all_products():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM products ORDER BY first_purchase_date DESC, batch_id").fetchall()
    conn.close()
    return rows


def get_product(batch_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM products WHERE batch_id = ?", (batch_id,)).fetchone()
    conn.close()
    return row


def update_product(batch_id, **kwargs):
    conn = get_connection()
    set_clause = ", ".join(f"{k} = ?" for k in kwargs)
    values = list(kwargs.values()) + [batch_id]
    conn.execute(f"UPDATE products SET {set_clause} WHERE batch_id = ?", values)
    conn.commit()
    conn.close()


def delete_product(batch_id):
    conn = get_connection()
    conn.execute("DELETE FROM products WHERE batch_id = ?", (batch_id,))
    conn.commit()
    conn.close()


def get_product_categories():
    conn = get_connection()
    rows = conn.execute("SELECT DISTINCT category FROM products ORDER BY category").fetchall()
    conn.close()
    return [r["category"] for r in rows]


def generate_batch_id(category_prefix="SR"):
    conn = get_connection()
    now = datetime.now()
    month_str = now.strftime("%b").upper()[:3]
    year_str = now.strftime("%y")
    suffix = f"{month_str}{year_str}"

    row = conn.execute(
        "SELECT batch_id FROM products WHERE batch_id LIKE ? ORDER BY batch_id DESC LIMIT 1",
        (f"{category_prefix}%{suffix}",)
    ).fetchone()

    if row:
        num_part = row["batch_id"].replace(suffix, "").replace(category_prefix, "")
        try:
            next_num = int(num_part) + 1
        except ValueError:
            next_num = 1
    else:
        all_rows = conn.execute(
            "SELECT batch_id FROM products WHERE batch_id LIKE ? ORDER BY batch_id DESC LIMIT 1",
            (f"{category_prefix}%",)
        ).fetchone()
        if all_rows:
            num_part = ""
            for ch in all_rows["batch_id"][len(category_prefix):]:
                if ch.isdigit():
                    num_part += ch
                else:
                    break
            try:
                next_num = int(num_part) + 1
            except ValueError:
                next_num = 1
        else:
            next_num = 1

    conn.close()
    return f"{category_prefix}{next_num:04d}{suffix}"


# --------------- Purchases ---------------

def add_purchase(date_val, batch_id, supplier_name, quantity, cost_per_unit,
                 payment_method="Cash", remarks=None):
    conn = get_connection()
    conn.execute(
        """INSERT INTO purchases (date, batch_id, supplier_name, quantity, cost_per_unit,
           payment_method, remarks) VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (date_val, batch_id, supplier_name, quantity, cost_per_unit, payment_method, remarks)
    )
    conn.commit()
    conn.close()


def get_all_purchases(start_date=None, end_date=None):
    conn = get_connection()
    query = """SELECT p.*, pr.product_name, pr.category
               FROM purchases p
               LEFT JOIN products pr ON p.batch_id = pr.batch_id"""
    params = []
    if start_date and end_date:
        query += " WHERE p.date BETWEEN ? AND ?"
        params = [start_date, end_date]
    query += " ORDER BY p.date DESC, p.id DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def get_total_purchased(batch_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT COALESCE(SUM(quantity), 0) as total FROM purchases WHERE batch_id = ?",
        (batch_id,)
    ).fetchone()
    conn.close()
    return row["total"]


# --------------- Sales ---------------

def add_sale(date_val, batch_id, quantity, selling_price_customer,
             selling_price_retailer, sale_type="Direct", remarks=None):
    conn = get_connection()
    conn.execute(
        """INSERT INTO sales (date, batch_id, quantity, selling_price_customer,
           selling_price_retailer, sale_type, remarks)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (date_val, batch_id, quantity, selling_price_customer,
         selling_price_retailer, sale_type, remarks)
    )
    conn.commit()
    conn.close()


def get_all_sales(start_date=None, end_date=None, sale_type=None):
    conn = get_connection()
    query = """SELECT s.*, pr.product_name, pr.category, pr.cost_per_unit as product_cost
               FROM sales s
               LEFT JOIN products pr ON s.batch_id = pr.batch_id WHERE 1=1"""
    params = []
    if start_date and end_date:
        query += " AND s.date BETWEEN ? AND ?"
        params += [start_date, end_date]
    if sale_type:
        query += " AND s.sale_type = ?"
        params.append(sale_type)
    query += " ORDER BY s.date DESC, s.id DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def get_total_sold(batch_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT COALESCE(SUM(quantity), 0) as total FROM sales WHERE batch_id = ?",
        (batch_id,)
    ).fetchone()
    conn.close()
    return row["total"]


# --------------- Stock ---------------

def get_stock():
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            pr.batch_id,
            pr.product_name,
            pr.category,
            pr.cost_per_unit,
            COALESCE(purch.total_purchased, 0) as total_purchased,
            COALESCE(sl.total_sold, 0) as total_sold,
            (COALESCE(purch.total_purchased, 0) - COALESCE(sl.total_sold, 0)) as closing_stock,
            pr.cost_per_unit * (COALESCE(purch.total_purchased, 0) - COALESCE(sl.total_sold, 0)) as stock_value
        FROM products pr
        LEFT JOIN (
            SELECT batch_id, SUM(quantity) as total_purchased FROM purchases GROUP BY batch_id
        ) purch ON pr.batch_id = purch.batch_id
        LEFT JOIN (
            SELECT batch_id, SUM(quantity) as total_sold FROM sales GROUP BY batch_id
        ) sl ON pr.batch_id = sl.batch_id
        ORDER BY pr.batch_id
    """).fetchall()
    conn.close()
    return rows


def get_available_stock(batch_id):
    conn = get_connection()
    row = conn.execute("""
        SELECT
            COALESCE((SELECT SUM(quantity) FROM purchases WHERE batch_id = ?), 0) -
            COALESCE((SELECT SUM(quantity) FROM sales WHERE batch_id = ?), 0) as available
    """, (batch_id, batch_id)).fetchone()
    conn.close()
    return row["available"]


def get_in_stock_products():
    conn = get_connection()
    rows = conn.execute("""
        SELECT pr.batch_id, pr.product_name, pr.category, pr.cost_per_unit,
            (COALESCE(purch.total_purchased, 0) - COALESCE(sl.total_sold, 0)) as available
        FROM products pr
        LEFT JOIN (SELECT batch_id, SUM(quantity) as total_purchased FROM purchases GROUP BY batch_id) purch
            ON pr.batch_id = purch.batch_id
        LEFT JOIN (SELECT batch_id, SUM(quantity) as total_sold FROM sales GROUP BY batch_id) sl
            ON pr.batch_id = sl.batch_id
        WHERE (COALESCE(purch.total_purchased, 0) - COALESCE(sl.total_sold, 0)) > 0
        ORDER BY pr.product_name
    """).fetchall()
    conn.close()
    return rows


# --------------- Expenses ---------------

def add_expense(date_val, expense_type, description, amount):
    conn = get_connection()
    conn.execute(
        "INSERT INTO expenses (date, expense_type, description, amount) VALUES (?, ?, ?, ?)",
        (date_val, expense_type, description, amount)
    )
    conn.commit()
    conn.close()


def get_all_expenses(start_date=None, end_date=None):
    conn = get_connection()
    query = "SELECT * FROM expenses"
    params = []
    if start_date and end_date:
        query += " WHERE date BETWEEN ? AND ?"
        params = [start_date, end_date]
    query += " ORDER BY date DESC, id DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


# --------------- Cash Flow ---------------

def add_cash_flow(date_val, description, inflow=0, outflow=0,
                  pending_type="Receipt", status="Completed"):
    conn = get_connection()
    conn.execute(
        """INSERT INTO cash_flow (date, description, inflow, outflow, pending_type, status)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (date_val, description, inflow, outflow, pending_type, status)
    )
    conn.commit()
    conn.close()


def get_all_cash_flow():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM cash_flow ORDER BY date ASC, id ASC").fetchall()
    conn.close()
    return rows


def update_cash_flow_status(cf_id, status):
    conn = get_connection()
    conn.execute("UPDATE cash_flow SET status = ? WHERE id = ?", (status, cf_id))
    conn.commit()
    conn.close()


def get_cash_summary():
    conn = get_connection()
    row = conn.execute("""
        SELECT
            COALESCE(SUM(CASE WHEN status='Completed' THEN inflow ELSE 0 END), 0) -
            COALESCE(SUM(CASE WHEN status='Completed' THEN outflow ELSE 0 END), 0) as cash_in_hand,
            COALESCE(SUM(CASE WHEN status='Pending' AND inflow > 0 THEN inflow ELSE 0 END), 0) as pending_receipts,
            COALESCE(SUM(CASE WHEN status='Pending' AND outflow > 0 THEN outflow ELSE 0 END), 0) as pending_payments
        FROM cash_flow
    """).fetchone()
    conn.close()
    return row


# --------------- Capital ---------------

def add_capital(date_val, description, cap_type, amount):
    conn = get_connection()
    conn.execute(
        "INSERT INTO capital (date, description, type, amount) VALUES (?, ?, ?, ?)",
        (date_val, description, cap_type, amount)
    )
    conn.commit()
    conn.close()


def get_all_capital():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM capital ORDER BY date ASC, id ASC").fetchall()
    conn.close()
    return rows


def get_capital_balance():
    conn = get_connection()
    row = conn.execute("""
        SELECT COALESCE(SUM(CASE WHEN type='Capital In' THEN amount ELSE -amount END), 0) as balance
        FROM capital
    """).fetchone()
    conn.close()
    return row["balance"]


# --------------- Reports / Aggregations ---------------

def get_monthly_pnl():
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            strftime('%Y-%m', s.date) as month,
            COALESCE(SUM((s.selling_price_retailer - pr.cost_per_unit) * s.quantity), 0) as gross_profit,
            0 as expenses,
            0 as net_profit
        FROM sales s
        LEFT JOIN products pr ON s.batch_id = pr.batch_id
        GROUP BY strftime('%Y-%m', s.date)
        ORDER BY month
    """).fetchall()

    result = []
    for r in rows:
        month = r["month"]
        gross = r["gross_profit"]
        exp_row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) as total FROM expenses WHERE strftime('%Y-%m', date) = ?",
            (month,)
        ).fetchone()
        expenses = exp_row["total"]
        result.append({
            "month": month,
            "gross_profit": gross,
            "expenses": expenses,
            "net_profit": gross - expenses
        })

    conn.close()
    return result


def get_monthly_revenue():
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            strftime('%Y-%m', date) as month,
            SUM(selling_price_retailer * quantity) as revenue,
            SUM(quantity) as units_sold
        FROM sales
        GROUP BY strftime('%Y-%m', date)
        ORDER BY month
    """).fetchall()
    conn.close()
    return rows


def get_top_selling_products(limit=5):
    conn = get_connection()
    rows = conn.execute("""
        SELECT s.batch_id, pr.product_name, SUM(s.quantity) as total_qty,
               SUM(s.selling_price_retailer * s.quantity) as total_revenue
        FROM sales s
        LEFT JOIN products pr ON s.batch_id = pr.batch_id
        GROUP BY s.batch_id
        ORDER BY total_qty DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return rows


def get_dashboard_kpis():
    conn = get_connection()

    total_products = conn.execute("SELECT COUNT(*) as c FROM products").fetchone()["c"]

    stock_value = conn.execute("""
        SELECT COALESCE(SUM(
            pr.cost_per_unit * (COALESCE(purch.tp, 0) - COALESCE(sl.ts, 0))
        ), 0) as val
        FROM products pr
        LEFT JOIN (SELECT batch_id, SUM(quantity) as tp FROM purchases GROUP BY batch_id) purch
            ON pr.batch_id = purch.batch_id
        LEFT JOIN (SELECT batch_id, SUM(quantity) as ts FROM sales GROUP BY batch_id) sl
            ON pr.batch_id = sl.batch_id
    """).fetchone()["val"]

    now = datetime.now()
    month_start = now.strftime("%Y-%m-01")
    month_end = now.strftime("%Y-%m-31")

    monthly_revenue = conn.execute(
        "SELECT COALESCE(SUM(selling_price_retailer * quantity), 0) as rev FROM sales WHERE date BETWEEN ? AND ?",
        (month_start, month_end)
    ).fetchone()["rev"]

    monthly_cost = conn.execute("""
        SELECT COALESCE(SUM(pr.cost_per_unit * s.quantity), 0) as cost
        FROM sales s LEFT JOIN products pr ON s.batch_id = pr.batch_id
        WHERE s.date BETWEEN ? AND ?
    """, (month_start, month_end)).fetchone()["cost"]

    monthly_expenses = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) as exp FROM expenses WHERE date BETWEEN ? AND ?",
        (month_start, month_end)
    ).fetchone()["exp"]

    monthly_profit = monthly_revenue - monthly_cost - monthly_expenses

    cash_summary = get_cash_summary()

    conn.close()
    return {
        "total_products": total_products,
        "stock_value": stock_value,
        "monthly_revenue": monthly_revenue,
        "monthly_profit": monthly_profit,
        "cash_in_hand": cash_summary["cash_in_hand"],
    }


def get_recent_sales(limit=5):
    conn = get_connection()
    rows = conn.execute("""
        SELECT s.date, s.batch_id, pr.product_name, s.quantity,
               s.selling_price_customer, s.sale_type
        FROM sales s LEFT JOIN products pr ON s.batch_id = pr.batch_id
        ORDER BY s.date DESC, s.id DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return rows


def get_recent_purchases(limit=5):
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.date, p.batch_id, pr.product_name, p.quantity, p.cost_per_unit
        FROM purchases p LEFT JOIN products pr ON p.batch_id = pr.batch_id
        ORDER BY p.date DESC, p.id DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return rows


def get_low_stock_alerts(threshold=1):
    conn = get_connection()
    rows = conn.execute("""
        SELECT pr.batch_id, pr.product_name,
            (COALESCE(purch.tp, 0) - COALESCE(sl.ts, 0)) as closing_stock
        FROM products pr
        LEFT JOIN (SELECT batch_id, SUM(quantity) as tp FROM purchases GROUP BY batch_id) purch
            ON pr.batch_id = purch.batch_id
        LEFT JOIN (SELECT batch_id, SUM(quantity) as ts FROM sales GROUP BY batch_id) sl
            ON pr.batch_id = sl.batch_id
        WHERE (COALESCE(purch.tp, 0) - COALESCE(sl.ts, 0)) <= ?
          AND (COALESCE(purch.tp, 0) - COALESCE(sl.ts, 0)) >= 0
        ORDER BY closing_stock ASC
    """, (threshold,)).fetchall()
    conn.close()
    return rows


def is_db_empty():
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) as c FROM products").fetchone()["c"]
    conn.close()
    return count == 0
