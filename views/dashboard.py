import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import database as db
import theme


def render():
    theme.page_header("Dashboard", "Business overview at a glance")

    st.markdown("")

    # --- KPI Cards ---
    kpis = db.get_dashboard_kpis()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Products", kpis["total_products"])
    c2.metric("Stock Value", f"Rs. {kpis['stock_value']:,.0f}")
    c3.metric("Monthly Revenue", f"Rs. {kpis['monthly_revenue']:,.0f}")
    c4.metric("Monthly Profit", f"Rs. {kpis['monthly_profit']:,.0f}")
    c5.metric("Cash in Hand", f"Rs. {kpis['cash_in_hand']:,.0f}")

    st.markdown("")
    st.markdown("")

    # --- Charts Row ---
    col_left, col_right = st.columns(2)

    with col_left:
        theme.section_header("Monthly Sales Trend")
        monthly = db.get_monthly_revenue()
        if monthly:
            df_monthly = pd.DataFrame([dict(r) for r in monthly])
            fig = px.bar(
                df_monthly, x="month", y="revenue",
                labels={"month": "Month", "revenue": "Revenue (Rs.)"},
                color_discrete_sequence=[theme.COLORS["accent"]],
            )
            fig.update_layout(
                margin=dict(l=0, r=0, t=10, b=0), height=300,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter"),
            )
            fig.update_xaxes(gridcolor=theme.COLORS["border_light"])
            fig.update_yaxes(gridcolor=theme.COLORS["border_light"])
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No sales data yet.")

    with col_right:
        theme.section_header("Top Selling Products")
        top = db.get_top_selling_products(5)
        if top:
            df_top = pd.DataFrame([dict(r) for r in top])
            fig = px.bar(
                df_top, x="total_qty", y="product_name", orientation="h",
                labels={"total_qty": "Units Sold", "product_name": "Product"},
                color_discrete_sequence=[theme.COLORS["primary_light"]],
            )
            fig.update_layout(
                margin=dict(l=0, r=0, t=10, b=0), height=300,
                yaxis=dict(autorange="reversed"),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter"),
            )
            fig.update_xaxes(gridcolor=theme.COLORS["border_light"])
            fig.update_yaxes(gridcolor=theme.COLORS["border_light"])
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No sales data yet.")

    st.markdown("")

    # --- Stock Status ---
    theme.section_header("Stock Status")
    stock_data = db.get_stock()
    if stock_data:
        in_stock = sum(1 for s in stock_data if s["closing_stock"] > 0)
        out_stock = sum(1 for s in stock_data if s["closing_stock"] <= 0)
        fig = go.Figure(data=[go.Pie(
            labels=["In Stock", "Out of Stock"],
            values=[in_stock, out_stock],
            marker_colors=[theme.COLORS["success"], theme.COLORS["danger"]],
            hole=0.45,
            textfont=dict(family="Inter"),
        )])
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0), height=280,
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
        )
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No stock data yet.")

    st.markdown("")

    # --- Recent Activity ---
    col_x, col_y = st.columns(2)

    with col_x:
        theme.section_header("Recent Sales")
        recent_sales = db.get_recent_sales(5)
        if recent_sales:
            df_rs = pd.DataFrame([dict(r) for r in recent_sales])
            df_rs.columns = ["Date", "Batch ID", "Product", "Qty", "Price", "Type"]
            st.dataframe(df_rs, width="stretch", hide_index=True)
        else:
            st.info("No sales recorded yet.")

    with col_y:
        theme.section_header("Recent Purchases")
        recent_purch = db.get_recent_purchases(5)
        if recent_purch:
            df_rp = pd.DataFrame([dict(r) for r in recent_purch])
            df_rp.columns = ["Date", "Batch ID", "Product", "Qty", "Cost/Unit"]
            st.dataframe(df_rp, width="stretch", hide_index=True)
        else:
            st.info("No purchases recorded yet.")
