import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import database as db
import theme


def render():
    theme.page_header("Reports", "Profit & Loss, Capital, and Sales Analysis")

    tab1, tab2, tab3 = st.tabs(["📊 Profit & Loss", "💼 Capital Tracking", "📉 Sales Analysis"])

    # --- P&L Tab ---
    with tab1:
        st.markdown("### Monthly Profit & Loss")

        pnl = db.get_monthly_pnl()
        if pnl:
            data = []
            cumulative_profit = 0
            for row in pnl:
                cumulative_profit += row["net_profit"]
                data.append({
                    "Month": row["month"],
                    "Gross Profit": f"Rs. {row['gross_profit']:,.0f}",
                    "Expenses": f"Rs. {row['expenses']:,.0f}",
                    "Net Profit": f"Rs. {row['net_profit']:,.0f}",
                    "Cumulative": f"Rs. {cumulative_profit:,.0f}",
                    "_gross": row["gross_profit"],
                    "_net": row["net_profit"],
                    "_expenses": row["expenses"],
                })

            df = pd.DataFrame(data)
            st.dataframe(
                df[["Month", "Gross Profit", "Expenses", "Net Profit", "Cumulative"]],
                width="stretch", hide_index=True,
            )

            total_gross = sum(r["gross_profit"] for r in pnl)
            total_exp = sum(r["expenses"] for r in pnl)
            total_net = sum(r["net_profit"] for r in pnl)

            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Total Gross Profit", f"Rs. {total_gross:,.0f}")
            mc2.metric("Total Expenses", f"Rs. {total_exp:,.0f}")
            mc3.metric("Total Net Profit", f"Rs. {total_net:,.0f}")

            # P&L Chart
            fig = go.Figure()
            months = [d["Month"] for d in data]
            fig.add_trace(go.Bar(
                x=months, y=[d["_gross"] for d in data],
                name="Gross Profit", marker_color=theme.COLORS["success"]
            ))
            fig.add_trace(go.Bar(
                x=months, y=[d["_expenses"] for d in data],
                name="Expenses", marker_color=theme.COLORS["danger"]
            ))
            fig.add_trace(go.Scatter(
                x=months, y=[d["_net"] for d in data],
                name="Net Profit", mode="lines+markers",
                line=dict(color=theme.COLORS["accent"], width=3),
            ))
            fig.update_layout(
                barmode="group", height=350,
                margin=dict(l=0, r=0, t=30, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
            )
            st.plotly_chart(fig, width="stretch")

            # Export
            csv = df[["Month", "Gross Profit", "Expenses", "Net Profit", "Cumulative"]].to_csv(index=False)
            st.download_button("📥 Export P&L to CSV", csv, "lookiva_pnl.csv", "text/csv")
        else:
            st.info("No sales data yet to generate P&L report.")

    # --- Capital Tracking Tab ---
    with tab2:
        st.markdown("### Capital Tracking")

        balance = db.get_capital_balance()
        st.metric("Current Capital Balance", f"Rs. {balance:,.0f}")

        capital = db.get_all_capital()
        if capital:
            data = []
            running = 0
            for c in capital:
                if c["type"] == "Capital In":
                    running += c["amount"]
                else:
                    running -= c["amount"]
                data.append({
                    "Date": c["date"],
                    "Description": c["description"],
                    "Type": c["type"],
                    "Amount": f"Rs. {c['amount']:,.0f}",
                    "Balance": f"Rs. {running:,.0f}",
                })

            df = pd.DataFrame(data)
            st.dataframe(df, width="stretch", hide_index=True)
        else:
            st.info("No capital entries found.")

        # Add capital entry
        st.markdown("---")
        with st.expander("➕ Add Capital Entry"):
            with st.form("capital_form", clear_on_submit=True):
                from datetime import date as dt_date
                col1, col2 = st.columns(2)
                with col1:
                    cap_date = st.date_input("Date", value=dt_date.today(), key="cap_date")
                    description = st.text_input("Description", key="cap_desc")
                with col2:
                    cap_type = st.selectbox("Type", ["Capital In", "Withdrawal"])
                    amount = st.number_input("Amount (Rs.)", min_value=0.0, step=1000.0, key="cap_amt")

                if st.form_submit_button("Add", type="primary"):
                    if amount > 0 and description:
                        db.add_capital(str(cap_date), description, cap_type, amount)
                        st.success("Capital entry added!")
                        st.rerun()
                    else:
                        st.error("Please fill in all fields.")

    # --- Sales Analysis Tab ---
    with tab3:
        st.markdown("### Sales Analysis")

        all_sales = db.get_all_sales()
        if not all_sales:
            st.info("No sales data to analyze.")
            return

        df_sales = pd.DataFrame([dict(s) for s in all_sales])
        df_sales["date"] = pd.to_datetime(df_sales["date"])
        df_sales["revenue"] = df_sales["selling_price_retailer"] * df_sales["quantity"]
        df_sales["margin"] = (df_sales["selling_price_retailer"] - df_sales["product_cost"].fillna(0)) * df_sales["quantity"]

        # By Channel
        st.markdown("#### Revenue by Channel")
        by_channel = df_sales.groupby("sale_type").agg(
            Revenue=("revenue", "sum"),
            Units=("quantity", "sum"),
            Margin=("margin", "sum"),
        ).reset_index()
        by_channel.columns = ["Channel", "Revenue (Rs.)", "Units Sold", "Margin (Rs.)"]

        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(by_channel, width="stretch", hide_index=True)
        with col2:
            fig = px.pie(by_channel, values="Revenue (Rs.)", names="Channel",
                         color_discrete_sequence=[theme.COLORS["accent"], theme.COLORS["primary_light"]])
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=250)
            st.plotly_chart(fig, width="stretch")

        # By Product
        st.markdown("#### Revenue by Product")
        by_product = df_sales.groupby("product_name").agg(
            Revenue=("revenue", "sum"),
            Units=("quantity", "sum"),
            Margin=("margin", "sum"),
        ).sort_values("Revenue", ascending=False).reset_index()
        by_product.columns = ["Product", "Revenue (Rs.)", "Units Sold", "Margin (Rs.)"]
        st.dataframe(by_product, width="stretch", hide_index=True)

        fig2 = px.bar(by_product.head(10), x="Product", y="Revenue (Rs.)",
                      color_discrete_sequence=[theme.COLORS["accent"]])
        fig2.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300)
        st.plotly_chart(fig2, width="stretch")

        # Monthly Trend
        st.markdown("#### Monthly Revenue Trend")
        df_sales["month"] = df_sales["date"].dt.to_period("M").astype(str)
        by_month = df_sales.groupby(["month", "sale_type"])["revenue"].sum().reset_index()
        fig3 = px.bar(by_month, x="month", y="revenue", color="sale_type",
                      labels={"month": "Month", "revenue": "Revenue (Rs.)", "sale_type": "Channel"},
                      barmode="group",
                      color_discrete_sequence=[theme.COLORS["accent"], theme.COLORS["primary_light"]])
        fig3.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300)
        st.plotly_chart(fig3, width="stretch")

        # Export
        csv = by_product.to_csv(index=False)
        st.download_button("📥 Export Sales Analysis", csv, "lookiva_sales_analysis.csv", "text/csv")
