import streamlit as st
import pandas as pd
from datetime import date, timedelta
import database as db
import theme


def render():
    theme.page_header("Purchases", "Record and track stock purchases")

    # --- Record New Purchase ---
    with st.expander("➕ Record New Purchase", expanded=True):
        products = db.get_all_products()

        if not products:
            st.warning("No products found. Please add products first in the Products page.")
            return

        with st.form("purchase_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                purchase_date = st.date_input("Purchase Date", value=date.today())
                product_options = {f"{p['batch_id']} - {p['product_name']}": p for p in products}
                selected = st.selectbox("Product", list(product_options.keys()))
                product = product_options[selected]
                supplier = st.text_input("Supplier Name", value=product["source"] or "")

            with col2:
                quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
                cost_per_unit = st.number_input("Cost Per Unit (Rs.)",
                                                 min_value=0.0,
                                                 value=float(product["cost_per_unit"]),
                                                 step=50.0)
                payment_method = st.selectbox("Payment Method", ["Cash", "Bank Transfer", "Credit"])

            remarks = st.text_input("Remarks (optional)")

            total = quantity * cost_per_unit
            st.info(f"**Total Purchase Cost: Rs. {total:,.0f}**")

            submitted = st.form_submit_button("Record Purchase", type="primary")

            if submitted:
                try:
                    db.add_purchase(
                        date_val=str(purchase_date),
                        batch_id=product["batch_id"],
                        supplier_name=supplier or "Unknown",
                        quantity=quantity,
                        cost_per_unit=cost_per_unit,
                        payment_method=payment_method,
                        remarks=remarks or None,
                    )
                    st.success(f"Purchase recorded: {quantity}x {product['product_name']} for Rs. {total:,.0f}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    # --- Purchase History ---
    st.markdown("### Purchase History")

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        start = st.date_input("From", value=date.today() - timedelta(days=90), key="purch_start")
    with col_d2:
        end = st.date_input("To", value=date.today(), key="purch_end")

    purchases = db.get_all_purchases(str(start), str(end))

    if purchases:
        data = []
        total_cost = 0
        for p in purchases:
            cost = p["quantity"] * p["cost_per_unit"]
            total_cost += cost
            data.append({
                "Date": p["date"],
                "Batch ID": p["batch_id"],
                "Product": p["product_name"] or p["batch_id"],
                "Supplier": p["supplier_name"],
                "Qty": p["quantity"],
                "Cost/Unit": f"Rs. {p['cost_per_unit']:,.0f}",
                "Total": f"Rs. {cost:,.0f}",
                "Payment": p["payment_method"],
            })

        df = pd.DataFrame(data)
        st.dataframe(df, width="stretch", hide_index=True)

        st.metric("Total Purchases in Period", f"Rs. {total_cost:,.0f}")

        # Monthly Summary
        st.markdown("#### Monthly Purchase Summary")
        df_summary = pd.DataFrame([dict(r) for r in purchases])
        df_summary["date"] = pd.to_datetime(df_summary["date"])
        df_summary["total"] = df_summary["quantity"] * df_summary["cost_per_unit"]
        monthly = df_summary.groupby(df_summary["date"].dt.to_period("M"))["total"].sum().reset_index()
        monthly["date"] = monthly["date"].astype(str)
        monthly.columns = ["Month", "Total (Rs.)"]
        st.dataframe(monthly, width="stretch", hide_index=True)
    else:
        st.info("No purchases found for the selected date range.")
