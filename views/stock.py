import streamlit as st
import pandas as pd
import database as db
import theme


def render():
    theme.page_header("Stock / Inventory", "Real-time inventory overview")

    stock = db.get_stock()

    if not stock:
        st.info("No stock data. Add products and record purchases to see inventory.")
        return

    # --- Summary Metrics ---
    total_items = sum(s["closing_stock"] for s in stock if s["closing_stock"] > 0)
    total_value = sum(s["stock_value"] for s in stock if s["closing_stock"] > 0)
    in_stock_count = sum(1 for s in stock if s["closing_stock"] > 0)
    out_stock_count = sum(1 for s in stock if s["closing_stock"] <= 0)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Units in Stock", f"{total_items}")
    c2.metric("Total Stock Value", f"Rs. {total_value:,.0f}")
    c3.metric("Products In Stock", in_stock_count)
    c4.metric("Out of Stock", out_stock_count)

    st.markdown("---")

    # --- Filter ---
    show = st.radio("Show", ["All", "In Stock Only", "Out of Stock Only"], horizontal=True)

    # --- Stock Table ---
    data = []
    for s in stock:
        closing = s["closing_stock"]

        if show == "In Stock Only" and closing <= 0:
            continue
        if show == "Out of Stock Only" and closing > 0:
            continue

        if closing <= 0:
            status = "🔴 Out of Stock"
        elif closing <= 2:
            status = "🟡 Low Stock"
        else:
            status = "🟢 Available"

        data.append({
            "Batch ID": s["batch_id"],
            "Product": s["product_name"],
            "Category": s["category"],
            "Purchased": s["total_purchased"],
            "Sold": s["total_sold"],
            "Closing Stock": closing,
            "Cost/Unit": f"Rs. {s['cost_per_unit']:,.0f}",
            "Stock Value": f"Rs. {s['stock_value']:,.0f}" if closing > 0 else "-",
            "Status": status,
        })

    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, width="stretch", hide_index=True)

        st.caption(f"Showing {len(data)} products")

        # --- Export ---
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Export to CSV",
            csv,
            "lookiva_stock.csv",
            "text/csv",
        )
    else:
        st.info("No products match the selected filter.")
