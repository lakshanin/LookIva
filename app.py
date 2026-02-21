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

st.markdown("""
<style>
/* Remove top padding from main page */
.block-container {
    padding-top: 1.5rem !important;
}

/* If still too much space, reduce more */
.main > div {
    padding-top: 0rem !important;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# 🔥 HEADER SECTION (Logo + Title)
# ============================================================

logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")

# --- Centered Logo ---
if os.path.exists(logo_path):
    st.image(logo_path, width=160)

# --- Title ---
st.markdown(f"""
<div style="text-align:left; margin-top: 10px;">
    <div style="font-family: {theme.FONTS['heading']}; 
                font-size: 2rem;
                color: {theme.COLORS['accent']}; 
                font-weight: 700;">
        LookIva Business Manager
    </div>
    <div style="font-family: {theme.FONTS['body']}; 
                font-size: 0.9rem;
                color: {theme.COLORS['accent_light']};">
        Timeless Sarees
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")


# ============================================================
# 🔥 TABS NAVIGATION
# ============================================================

tab_dashboard, tab_products, tab_purchases, tab_sales, tab_stock, tab_expenses, tab_cashflow, tab_reports = st.tabs([
    "📊 Dashboard",
    "📦 Products",
    "🛒 Purchases",
    "💰 Sales",
    "📋 Stock",
    "💸 Expenses",
    "🏦 Cash Flow",
    "📈 Reports",
])


# ============================================================
# 🔥 TAB ROUTING
# ============================================================

with tab_dashboard:
    from views import dashboard
    dashboard.render()

with tab_products:
    from views import products
    products.render()

with tab_purchases:
    from views import purchases
    purchases.render()

with tab_sales:
    from views import sales
    sales.render()

with tab_stock:
    from views import stock
    stock.render()

with tab_expenses:
    from views import expenses
    expenses.render()

with tab_cashflow:
    from views import cash_flow
    cash_flow.render()

with tab_reports:
    from views import reports
    reports.render()