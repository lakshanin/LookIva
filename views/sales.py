import streamlit as st
import pandas as pd
from datetime import date, timedelta
import database as db
import theme


def render():
    theme.page_header("Sales", "Record direct and indirect sales")

    # --- Record New Sale ---
    with st.expander("➕ Record New Sale", expanded=True):
        in_stock = db.get_in_stock_products()

        if not in_stock:
            st.warning("No products in stock! Record a purchase first.")
        else:
            with st.form("sale_form", clear_on_submit=True):
                col1, col2 = st.columns(2)

                with col1:
                    sale_date = st.date_input("Sale Date", value=date.today())
                    product_options = {
                        f"{p['batch_id']} - {p['product_name']} ({p['available']} available)": p
                        for p in in_stock
                    }
                    selected = st.selectbox("Product (in stock only)", list(product_options.keys()))
                    product = product_options[selected]

                    quantity = st.number_input("Quantity", min_value=1,
                                               max_value=int(product["available"]),
                                               value=1, step=1)

                with col2:
                    sale_type = st.radio("Sale Type", ["Indirect", "Direct"], horizontal=True,
                                          help="Indirect = sold through retailer friend. Direct = sold to customer yourself.")
                    selling_price_customer = st.number_input(
                        "Selling Price to Customer (Rs.)", min_value=0.0, step=50.0,
                        help="The price the end customer pays"
                    )

                    if sale_type == "Indirect":
                        selling_price_retailer = st.number_input(
                            "Your Price / Retailer Price (Rs.)", min_value=0.0, step=50.0,
                            help="The amount you (LookIva) receive from the retailer"
                        )
                    else:
                        selling_price_retailer = selling_price_customer

                remarks = st.text_input("Remarks (optional)")

                # Show margin preview
                cost = product["cost_per_unit"]
                margin = (selling_price_retailer - cost) * quantity
                revenue = selling_price_retailer * quantity

                st.markdown(f"""
                **Sale Preview:**
                - Cost per unit: Rs. {cost:,.0f}
                - Your revenue: Rs. {revenue:,.0f}
                - **Margin: Rs. {margin:,.0f}** {'✅' if margin > 0 else '⚠️'}
                """)

                submitted = st.form_submit_button("Record Sale", type="primary")

                if submitted:
                    if selling_price_customer <= 0:
                        st.error("Please enter a valid selling price!")
                    elif sale_type == "Indirect" and selling_price_retailer <= 0:
                        st.error("Please enter a valid retailer price!")
                    else:
                        try:
                            db.add_sale(
                                date_val=str(sale_date),
                                batch_id=product["batch_id"],
                                quantity=quantity,
                                selling_price_customer=selling_price_customer,
                                selling_price_retailer=selling_price_retailer,
                                sale_type=sale_type,
                                remarks=remarks or None,
                            )
                            st.success(f"Sale recorded: {quantity}x {product['product_name']} — Margin: Rs. {margin:,.0f}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

    # --- Sales History ---
    st.markdown("### Sales History")

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        start = st.date_input("From", value=date.today() - timedelta(days=90), key="sale_start")
    with col_f2:
        end = st.date_input("To", value=date.today(), key="sale_end")
    with col_f3:
        type_filter = st.selectbox("Sale Type", ["All", "Direct", "Indirect"])

    sale_type_filter = None if type_filter == "All" else type_filter
    sales = db.get_all_sales(str(start), str(end), sale_type_filter)

    if sales:
        data = []
        total_revenue = 0
        total_margin = 0
        for s in sales:
            cost = s["product_cost"] or 0
            margin = (s["selling_price_retailer"] - cost) * s["quantity"]
            revenue = s["selling_price_retailer"] * s["quantity"]
            total_revenue += revenue
            total_margin += margin
            data.append({
                "Date": s["date"],
                "Batch ID": s["batch_id"],
                "Product": s["product_name"] or s["batch_id"],
                "Qty": s["quantity"],
                "Customer Price": f"Rs. {s['selling_price_customer']:,.0f}",
                "Your Price": f"Rs. {s['selling_price_retailer']:,.0f}",
                "Margin": f"Rs. {margin:,.0f}",
                "Type": s["sale_type"],
            })

        df = pd.DataFrame(data)
        st.dataframe(df, width="stretch", hide_index=True)

        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Total Sales", len(data))
        mc2.metric("Total Revenue", f"Rs. {total_revenue:,.0f}")
        mc3.metric("Total Margin", f"Rs. {total_margin:,.0f}")
    else:
        st.info("No sales found for the selected filters.")
