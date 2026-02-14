import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
import database as db
import theme


def render():
    theme.page_header("Expenses", "Track business expenses")

    # --- Add New Expense ---
    with st.expander("➕ Add New Expense", expanded=True):
        with st.form("expense_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                expense_date = st.date_input("Date", value=date.today())
                expense_type = st.selectbox("Expense Type",
                                             ["Transport", "Packaging", "Marketing", "Rent", "Phone", "Other"])
            with col2:
                description = st.text_input("Description", placeholder="e.g., Petta trip, packaging materials")
                amount = st.number_input("Amount (Rs.)", min_value=0.0, step=50.0)

            submitted = st.form_submit_button("Add Expense", type="primary")

            if submitted:
                if amount <= 0:
                    st.error("Please enter a valid amount!")
                else:
                    try:
                        db.add_expense(
                            date_val=str(expense_date),
                            expense_type=expense_type,
                            description=description or expense_type,
                            amount=amount,
                        )
                        st.success(f"Expense recorded: {expense_type} — Rs. {amount:,.0f}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    # --- Expense History ---
    st.markdown("### Expense History")

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        start = st.date_input("From", value=date.today() - timedelta(days=90), key="exp_start")
    with col_d2:
        end = st.date_input("To", value=date.today(), key="exp_end")

    expenses = db.get_all_expenses(str(start), str(end))

    if expenses:
        data = []
        total = 0
        for e in expenses:
            total += e["amount"]
            data.append({
                "Date": e["date"],
                "Type": e["expense_type"],
                "Description": e["description"],
                "Amount": f"Rs. {e['amount']:,.0f}",
            })

        df = pd.DataFrame(data)
        st.dataframe(df, width="stretch", hide_index=True)
        st.metric("Total Expenses", f"Rs. {total:,.0f}")

        # --- By Type Chart ---
        st.markdown("#### Expenses by Type")
        df_chart = pd.DataFrame([dict(e) for e in expenses])
        by_type = df_chart.groupby("expense_type")["amount"].sum().reset_index()
        by_type.columns = ["Type", "Amount"]
        fig = px.pie(by_type, values="Amount", names="Type",
                     color_discrete_sequence=[theme.COLORS["accent"], theme.COLORS["primary_light"], theme.COLORS["info"], theme.COLORS["success"], theme.COLORS["warning"], theme.COLORS["danger"]])
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300)
        st.plotly_chart(fig, width="stretch")

        # --- Monthly Trend ---
        st.markdown("#### Monthly Expense Trend")
        df_chart["date"] = pd.to_datetime(df_chart["date"])
        monthly = df_chart.groupby(df_chart["date"].dt.to_period("M"))["amount"].sum().reset_index()
        monthly["date"] = monthly["date"].astype(str)
        monthly.columns = ["Month", "Amount"]
        fig2 = px.bar(monthly, x="Month", y="Amount",
                      color_discrete_sequence=[theme.COLORS["danger"]])
        fig2.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300)
        st.plotly_chart(fig2, width="stretch")
    else:
        st.info("No expenses found for the selected date range.")
