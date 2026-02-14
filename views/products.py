import streamlit as st
import pandas as pd
import os
from datetime import date
import database as db
import theme

IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "products")


def _save_image(uploaded_file, batch_id):
    """Save uploaded image and return the relative path."""
    os.makedirs(IMAGES_DIR, exist_ok=True)
    ext = os.path.splitext(uploaded_file.name)[1] or ".png"
    filename = f"{batch_id}{ext}"
    filepath = os.path.join(IMAGES_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return filepath


def render():
    theme.page_header("Product Master", "Manage your product catalog")

    # --- Add New Product ---
    with st.expander("➕ Add New Product", expanded=False):
        # Image uploader outside form (st.file_uploader doesn't reset well inside forms)
        uploaded_image = st.file_uploader(
            "Product Image (optional)",
            type=["png", "jpg", "jpeg", "webp"],
            key="add_product_image",
        )
        if uploaded_image:
            st.image(uploaded_image, width=150, caption="Preview")

        with st.form("add_product_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)

            with col1:
                batch_id = st.text_input("Batch ID", value=db.generate_batch_id(),
                                         help="Auto-generated. You can modify if needed.")
                base_product_id = st.text_input("Base Product ID", placeholder="e.g., SR0050")
                category = st.selectbox("Category", ["Saree", "USkirt", "Blouse", "Other"])

            with col2:
                product_name = st.text_input("Product Name *", placeholder="e.g., Indian Bathik Saree")
                fabric = st.text_input("Fabric", placeholder="e.g., Cotton, Silk")
                color = st.text_input("Color", placeholder="e.g., Red, Blue")

            with col3:
                pattern = st.text_input("Pattern", placeholder="e.g., Printed, Embroidered")
                source = st.text_input("Source / Supplier", placeholder="e.g., Petta")
                cost_per_unit = st.number_input("Cost Per Unit (Rs.)", min_value=0.0, step=50.0)

            size = st.text_input("Size (optional)", placeholder="e.g., Free size")
            first_purchase_date = st.date_input("First Purchase Date", value=date.today())
            remarks = st.text_area("Remarks", placeholder="Any notes about this product...")

            submitted = st.form_submit_button("Add Product", type="primary")

            if submitted:
                if not product_name:
                    st.error("Product Name is required!")
                elif not batch_id:
                    st.error("Batch ID is required!")
                else:
                    try:
                        image_path = None
                        if uploaded_image:
                            image_path = _save_image(uploaded_image, batch_id)

                        if not base_product_id:
                            base_product_id = batch_id[:6]
                        db.add_product(
                            batch_id=batch_id,
                            base_product_id=base_product_id,
                            category=category,
                            product_name=product_name,
                            fabric=fabric or None,
                            color=color or None,
                            pattern=pattern or None,
                            size=size or None,
                            source=source or None,
                            cost_per_unit=cost_per_unit,
                            first_purchase_date=str(first_purchase_date),
                            image_path=image_path,
                            remarks=remarks or None,
                        )
                        st.success(f"Product '{product_name}' added successfully!")
                        st.rerun()
                    except Exception as e:
                        if "UNIQUE constraint" in str(e):
                            st.error(f"Batch ID '{batch_id}' already exists! Change it.")
                        else:
                            st.error(f"Error: {e}")

    # --- Filters ---
    st.markdown("### Product List")
    col_f1, col_f2 = st.columns([1, 3])
    with col_f1:
        categories = ["All"] + db.get_product_categories()
        filter_cat = st.selectbox("Filter by Category", categories)
    with col_f2:
        search = st.text_input("Search products", placeholder="Type product name or batch ID...")

    # --- Product Table ---
    products = db.get_all_products()
    if products:
        data = []
        for p in products:
            stock_qty = db.get_available_stock(p["batch_id"])
            status = "Active" if stock_qty > 0 else "Out of Stock"
            data.append({
                "Batch ID": p["batch_id"],
                "Category": p["category"],
                "Product Name": p["product_name"],
                "Fabric": p["fabric"] or "-",
                "Color": p["color"] or "-",
                "Source": p["source"] or "-",
                "Cost (Rs.)": f"{p['cost_per_unit']:,.0f}",
                "Stock": stock_qty,
                "Status": status,
            })

        df = pd.DataFrame(data)

        if filter_cat != "All":
            df = df[df["Category"] == filter_cat]

        if search:
            mask = (
                df["Product Name"].str.contains(search, case=False, na=False) |
                df["Batch ID"].str.contains(search, case=False, na=False)
            )
            df = df[mask]

        st.dataframe(
            df,
            width="stretch",
            hide_index=True,
            column_config={
                "Status": st.column_config.TextColumn(
                    "Status",
                    help="Active = in stock, Out of Stock = 0 remaining"
                ),
                "Stock": st.column_config.NumberColumn("Stock", format="%d"),
            },
        )
        st.caption(f"Showing {len(df)} of {len(data)} products")

        # --- View Product with Image ---
        st.markdown("---")
        with st.expander("🖼️ View Product Details"):
            product_options = {f"{p['batch_id']} - {p['product_name']}": p["batch_id"] for p in products}
            selected_view = st.selectbox("Select product", list(product_options.keys()), key="view_product")
            selected_view_id = product_options[selected_view]
            prod_view = db.get_product(selected_view_id)

            if prod_view:
                vc1, vc2 = st.columns([1, 2])
                with vc1:
                    if prod_view["image_path"] and os.path.exists(prod_view["image_path"]):
                        st.image(prod_view["image_path"], width=250)
                    else:
                        st.markdown("*No image uploaded*")
                with vc2:
                    st.markdown(f"**{prod_view['product_name']}**")
                    st.markdown(f"Batch ID: `{prod_view['batch_id']}`")
                    st.markdown(f"Category: {prod_view['category']}")
                    st.markdown(f"Fabric: {prod_view['fabric'] or '-'}")
                    st.markdown(f"Color: {prod_view['color'] or '-'}")
                    st.markdown(f"Pattern: {prod_view['pattern'] or '-'}")
                    st.markdown(f"Source: {prod_view['source'] or '-'}")
                    st.markdown(f"Cost: Rs. {prod_view['cost_per_unit']:,.0f}")
                    if prod_view['remarks']:
                        st.markdown(f"Remarks: {prod_view['remarks']}")
    else:
        st.info("No products found. Add your first product above!")

    # --- Edit Product ---
    st.markdown("---")
    with st.expander("✏️ Edit Product"):
        if products:
            product_options_edit = {f"{p['batch_id']} - {p['product_name']}": p["batch_id"] for p in products}
            selected = st.selectbox("Select product to edit", list(product_options_edit.keys()), key="edit_product")
            selected_id = product_options_edit[selected]
            prod = db.get_product(selected_id)

            if prod:
                # Image upload for edit (outside form)
                edit_image = st.file_uploader(
                    "Update Product Image",
                    type=["png", "jpg", "jpeg", "webp"],
                    key=f"edit_img_{selected_id}",
                )
                if edit_image:
                    st.image(edit_image, width=150, caption="New image preview")
                elif prod["image_path"] and os.path.exists(prod["image_path"]):
                    st.image(prod["image_path"], width=150, caption="Current image")

                with st.form("edit_product_form"):
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        new_name = st.text_input("Product Name", value=prod["product_name"])
                        new_fabric = st.text_input("Fabric", value=prod["fabric"] or "")
                        new_color = st.text_input("Color", value=prod["color"] or "")
                        new_source = st.text_input("Source", value=prod["source"] or "")
                    with ec2:
                        new_category = st.selectbox("Category",
                                                     ["Saree", "USkirt", "Blouse", "Other"],
                                                     index=["Saree", "USkirt", "Blouse", "Other"].index(prod["category"])
                                                     if prod["category"] in ["Saree", "USkirt", "Blouse", "Other"] else 0)
                        new_pattern = st.text_input("Pattern", value=prod["pattern"] or "")
                        new_cost = st.number_input("Cost Per Unit", value=float(prod["cost_per_unit"]), step=50.0)
                        new_remarks = st.text_input("Remarks", value=prod["remarks"] or "")

                    if st.form_submit_button("Update Product", type="primary"):
                        update_fields = dict(
                            product_name=new_name,
                            category=new_category,
                            fabric=new_fabric or None,
                            color=new_color or None,
                            pattern=new_pattern or None,
                            source=new_source or None,
                            cost_per_unit=new_cost,
                            remarks=new_remarks or None,
                        )
                        if edit_image:
                            update_fields["image_path"] = _save_image(edit_image, selected_id)

                        db.update_product(selected_id, **update_fields)
                        st.success("Product updated!")
                        st.rerun()
        else:
            st.info("No products to edit.")
