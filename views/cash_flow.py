import streamlit as st
import pandas as pd
from datetime import date
import database as db
import theme


def render():
    theme.page_header("Cash Flow", "Track money in and out")

    # --- Summary Cards ---
    summary = db.get_cash_summary()
    c1, c2, c3 = st.columns(3)
    c1.metric("Cash in Hand", f"Rs. {summary['cash_in_hand']:,.0f}")
    c2.metric("Pending Receipts", f"Rs. {summary['pending_receipts']:,.0f}")
    c3.metric("Pending Payments", f"Rs. {summary['pending_payments']:,.0f}")

    st.markdown("---")

    # --- Add New Entry ---
    with st.expander("➕ Add Cash Flow Entry", expanded=False):
        with st.form("cashflow_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                cf_date = st.date_input("Date", value=date.today())
                description = st.text_input("Description", placeholder="e.g., Retail sales, Stock purchase")
                flow_type = st.radio("Type", ["Inflow (Money In)", "Outflow (Money Out)"], horizontal=True)

            with col2:
                amount = st.number_input("Amount (Rs.)", min_value=0.0, step=100.0)
                pending_type = st.selectbox("Pending Type", ["Receipt", "Payment"])
                status = st.selectbox("Status", ["Completed", "Pending"])

            submitted = st.form_submit_button("Add Entry", type="primary")

            if submitted:
                if amount <= 0:
                    st.error("Please enter a valid amount!")
                elif not description:
                    st.error("Please enter a description!")
                else:
                    try:
                        inflow = amount if "Inflow" in flow_type else 0
                        outflow = amount if "Outflow" in flow_type else 0
                        db.add_cash_flow(
                            date_val=str(cf_date),
                            description=description,
                            inflow=inflow,
                            outflow=outflow,
                            pending_type=pending_type,
                            status=status,
                        )
                        st.success(f"Cash flow entry added: {description}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    # --- Cash Flow Table ---
    st.markdown("### Cash Flow Records")
    entries = db.get_all_cash_flow()

    if entries:
        data = []
        running_balance = 0
        for e in entries:
            inflow = e["inflow"] or 0
            outflow = e["outflow"] or 0
            net = inflow - outflow
            running_balance += net
            data.append({
                "Date": e["date"],
                "Description": e["description"],
                "Inflow": f"Rs. {inflow:,.0f}" if inflow > 0 else "-",
                "Outflow": f"Rs. {outflow:,.0f}" if outflow > 0 else "-",
                "Net": f"Rs. {net:,.0f}",
                "Balance": f"Rs. {running_balance:,.0f}",
                "Status": e["status"] or "Completed",
                "ID": e["id"],
            })

        df = pd.DataFrame(data)
        st.dataframe(df.drop(columns=["ID"]), width="stretch", hide_index=True)

        # --- Mark Pending as Completed ---
        pending = [d for d in data if d["Status"] == "Pending"]
        if pending:
            st.markdown("#### Update Pending Entries")
            for p in pending:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.text(f"{p['Date']} | {p['Description']} | {p['Inflow'] if p['Inflow'] != '-' else p['Outflow']}")
                with col_b:
                    if st.button("Mark Completed", key=f"complete_{p['ID']}"):
                        db.update_cash_flow_status(p["ID"], "Completed")
                        st.success("Updated!")
                        st.rerun()
    else:
        st.info("No cash flow entries found.")
