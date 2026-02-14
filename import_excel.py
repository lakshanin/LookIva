"""
One-time migration script to import data from SareeBusinessTracker.xlsx into SQLite.
Called automatically on first app launch if the database is empty.
"""
import os
import pandas as pd
from datetime import datetime
import database as db


EXCEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SareeBusinessTracker.xlsx")


def import_all():
    if not os.path.exists(EXCEL_PATH):
        return False

    if not db.is_db_empty():
        return False

    print("Importing data from Excel...")

    try:
        _import_products()
        _import_purchases()
        _import_sales()
        _import_expenses()
        _import_cash_flow()
        _import_capital()
        print("Import completed successfully!")
        return True
    except Exception as e:
        print(f"Import error: {e}")
        raise


def _import_products():
    df = pd.read_excel(EXCEL_PATH, sheet_name="ProductMaster")
    df = df.dropna(subset=["BatchID"])
    df = df[df["BatchID"].str.strip() != ""]

    conn = db.get_connection()
    count = 0
    for _, row in df.iterrows():
        batch_id = str(row.get("BatchID", "")).strip()
        if not batch_id:
            continue

        first_date = row.get("FirstPurchaseDate")
        if pd.notna(first_date):
            if isinstance(first_date, datetime):
                first_date = first_date.strftime("%Y-%m-%d")
            else:
                first_date = str(first_date)
        else:
            first_date = None

        conn.execute(
            """INSERT OR IGNORE INTO products
               (batch_id, base_product_id, category, product_name, fabric, color,
                pattern, size, source, cost_per_unit, first_purchase_date, remarks)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                batch_id,
                str(row.get("BaseProductID", "")).strip() or batch_id,
                str(row.get("ProductCategory", "Saree")).strip() or "Saree",
                str(row.get("ProductName", "")).strip(),
                _clean(row.get("Fabric")),
                _clean(row.get("Color")),
                _clean(row.get("Pattern")),
                _clean(row.get("Size")),
                _clean(row.get("Source")),
                float(row.get("CostPerUnit", 0) or 0),
                first_date,
                _clean(row.get("Remarks")),
            )
        )
        count += 1

    conn.commit()
    conn.close()
    print(f"  Products imported: {count}")


def _import_purchases():
    df = pd.read_excel(EXCEL_PATH, sheet_name="Purchases")
    df = df.dropna(subset=["BatchID"])
    df = df[df["BatchID"].str.strip() != ""]

    conn = db.get_connection()
    count = 0
    for _, row in df.iterrows():
        batch_id = str(row.get("BatchID", "")).strip()
        if not batch_id:
            continue

        date_val = row.get("Date")
        if pd.notna(date_val):
            if isinstance(date_val, datetime):
                date_val = date_val.strftime("%Y-%m-%d")
            else:
                date_val = str(date_val)
        else:
            continue

        quantity = int(row.get("Quantity", 0) or 0)
        if quantity <= 0:
            continue

        conn.execute(
            """INSERT INTO purchases (date, batch_id, supplier_name, quantity, cost_per_unit, payment_method, remarks)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                date_val,
                batch_id,
                _clean(row.get("SupplierName")) or "Unknown",
                quantity,
                float(row.get("CostPerUnit", 0) or 0),
                _clean(row.get("PaymentMethod")) or "Cash",
                _clean(row.get("Remarks")),
            )
        )
        count += 1

    conn.commit()
    conn.close()
    print(f"  Purchases imported: {count}")


def _import_sales():
    df = pd.read_excel(EXCEL_PATH, sheet_name="Sales")
    df = df.dropna(subset=["BatchID"])
    df = df[df["BatchID"].str.strip() != ""]

    conn = db.get_connection()
    count = 0
    for _, row in df.iterrows():
        batch_id = str(row.get("BatchID", "")).strip()
        if not batch_id:
            continue

        date_val = row.get("Date")
        if pd.notna(date_val):
            if isinstance(date_val, datetime):
                date_val = date_val.strftime("%Y-%m-%d")
            else:
                date_val = str(date_val)
        else:
            continue

        quantity = int(row.get("Quantity", 0) or 0)
        if quantity <= 0:
            continue

        price_customer = float(row.get("SellingPriceToCustomer", 0) or 0)
        price_retailer = float(row.get("SellingPriceToRetailer", 0) or 0)
        sale_type = str(row.get("SaleType", "Direct")).strip()
        if sale_type not in ("Direct", "Indirect"):
            sale_type = "Direct"

        if price_retailer == 0:
            price_retailer = price_customer

        conn.execute(
            """INSERT INTO sales (date, batch_id, quantity, selling_price_customer,
               selling_price_retailer, sale_type, remarks)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                date_val,
                batch_id,
                quantity,
                price_customer,
                price_retailer,
                sale_type,
                _clean(row.get("Remarks")),
            )
        )
        count += 1

    conn.commit()
    conn.close()
    print(f"  Sales imported: {count}")


def _import_expenses():
    df = pd.read_excel(EXCEL_PATH, sheet_name="OtherExpenses")
    df = df.dropna(subset=["Date"])

    conn = db.get_connection()
    count = 0
    for _, row in df.iterrows():
        date_val = row.get("Date")
        if pd.notna(date_val):
            if isinstance(date_val, datetime):
                date_val = date_val.strftime("%Y-%m-%d")
            else:
                date_val = str(date_val)
        else:
            continue

        amount = float(row.get("Amount", 0) or 0)
        if amount <= 0:
            continue

        conn.execute(
            "INSERT INTO expenses (date, expense_type, description, amount) VALUES (?, ?, ?, ?)",
            (
                date_val,
                _clean(row.get("ExpenseType")) or "Other",
                _clean(row.get("Description")) or "",
                amount,
            )
        )
        count += 1

    conn.commit()
    conn.close()
    print(f"  Expenses imported: {count}")


def _import_cash_flow():
    df = pd.read_excel(EXCEL_PATH, sheet_name="CashFlowTracker")
    df = df.dropna(subset=["Date"])

    conn = db.get_connection()
    count = 0
    for _, row in df.iterrows():
        date_val = row.get("Date")
        if pd.notna(date_val):
            if isinstance(date_val, datetime):
                date_val = date_val.strftime("%Y-%m-%d")
            else:
                date_val = str(date_val)
        else:
            continue

        description = _clean(row.get("Description")) or ""
        inflow = float(row.get("Inflow", 0) or 0)
        outflow = float(row.get("Outflow", 0) or 0)

        if inflow == 0 and outflow == 0:
            continue

        pending_type = _clean(row.get("Pending Type")) or "Receipt"
        status = _clean(row.get("Status")) or "Completed"

        conn.execute(
            """INSERT INTO cash_flow (date, description, inflow, outflow, pending_type, status)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (date_val, description, inflow, outflow, pending_type, status)
        )
        count += 1

    conn.commit()
    conn.close()
    print(f"  Cash flow imported: {count}")


def _import_capital():
    df = pd.read_excel(EXCEL_PATH, sheet_name="CapitalTracking")
    df = df.dropna(subset=["Date"])

    conn = db.get_connection()
    count = 0
    for _, row in df.iterrows():
        date_val = row.get("Date")
        if pd.notna(date_val):
            if isinstance(date_val, datetime):
                date_val = date_val.strftime("%Y-%m-%d")
            else:
                date_val = str(date_val)
        else:
            continue

        amount = float(row.get("Amount", 0) or 0)
        if amount <= 0:
            continue

        conn.execute(
            "INSERT INTO capital (date, description, type, amount) VALUES (?, ?, ?, ?)",
            (
                date_val,
                _clean(row.get("Description")) or "",
                _clean(row.get("Type")) or "Capital In",
                amount,
            )
        )
        count += 1

    conn.commit()
    conn.close()
    print(f"  Capital imported: {count}")


def _clean(val):
    if pd.isna(val) or val is None:
        return None
    s = str(val).strip()
    return s if s else None


if __name__ == "__main__":
    db.init_db()
    import_all()
