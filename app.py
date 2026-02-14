import streamlit as st
import os
import database as db
import import_excel
import theme

# --- Page Config ---
st.set_page_config(**theme.get_page_config())

# --- Initialize Database ---
db.init_db()

# --- Auto-import Excel data on first run ---
if db.is_db_empty():
    with st.spinner("Importing data from Excel..."):
        try:
            result = import_excel.import_all()
            if result:
                st.success("Excel data imported successfully!")
                st.rerun()
        except Exception as e:
            st.error(f"Import failed: {e}")

# --- Inject Enterprise Theme CSS ---
st.markdown(theme.inject_css(), unsafe_allow_html=True)

# --- Sidebar Navigation ---
with st.sidebar:
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=180)
    else:
        st.markdown(f"""
        <div style="text-align:center; padding: 20px 0 10px 0;">
            <div style="font-family: {theme.FONTS['heading']}; font-size: 1.6rem;
                        color: {theme.COLORS['accent']}; font-weight: 700;
                        letter-spacing: 0.15em;">LOOKIVA</div>
            <div style="font-family: {theme.FONTS['body']}; font-size: 0.7rem;
                        color: {theme.COLORS['accent_light']}; letter-spacing: 0.25em;
                        text-transform: uppercase; margin-top: 2px;">Timeless Sarees</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "📦 Products",
            "🛒 Purchases",
            "💰 Sales",
            "📋 Stock",
            "💸 Expenses",
            "🏦 Cash Flow",
            "📈 Reports",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.caption("LookIva Business Manager v1.0")

# --- Page Routing ---
if page == "📊 Dashboard":
    from views import dashboard
    dashboard.render()
elif page == "📦 Products":
    from views import products
    products.render()
elif page == "🛒 Purchases":
    from views import purchases
    purchases.render()
elif page == "💰 Sales":
    from views import sales
    sales.render()
elif page == "📋 Stock":
    from views import stock
    stock.render()
elif page == "💸 Expenses":
    from views import expenses
    expenses.render()
elif page == "🏦 Cash Flow":
    from views import cash_flow
    cash_flow.render()
elif page == "📈 Reports":
    from views import reports
    reports.render()
