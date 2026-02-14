"""
LookIva Enterprise UI/UX Theme Framework
Brand Identity: Elegant, Premium, Timeless
Palette: Charcoal, Gold, Cream, Warm White
"""

# --- Brand Colors ---
COLORS = {
    "primary": "#2C2C2C",         # Charcoal - main text, headers
    "primary_light": "#4A4A4A",   # Lighter charcoal
    "accent": "#C8A96E",          # Gold - accent, highlights, CTAs
    "accent_dark": "#A8893E",     # Darker gold - hover states
    "accent_light": "#E8D5A8",    # Light gold - subtle backgrounds
    "background": "#FAF8F5",      # Warm cream - main background
    "surface": "#FFFFFF",         # White - cards, panels
    "surface_alt": "#F5F0E8",     # Cream tint - alternate rows, sections
    "border": "#E8E0D4",          # Warm border
    "border_light": "#F0EBE3",    # Subtle dividers
    "text": "#2C2C2C",            # Primary text
    "text_secondary": "#7A7468",  # Secondary/muted text
    "text_light": "#A09888",      # Placeholder text
    "success": "#5B8C5A",         # Muted green
    "warning": "#D4A843",         # Warm amber
    "danger": "#C45B5B",          # Muted red
    "info": "#6B8EAE",            # Muted blue
}

# --- Typography ---
FONTS = {
    "heading": "'Playfair Display', Georgia, 'Times New Roman', serif",
    "body": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    "mono": "'JetBrains Mono', 'Fira Code', monospace",
}


def get_page_config():
    return {
        "page_title": "LookIva - Business Manager",
        "page_icon": "👗",
        "layout": "wide",
        "initial_sidebar_state": "expanded",
    }


def inject_css():
    """Returns the full CSS string to inject into Streamlit."""
    return f"""
<style>
    /* === GOOGLE FONTS === */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

    /* === GLOBAL === */
    .stApp {{
        background-color: {COLORS['background']};
    }}

    /* Hide default Streamlit header/footer */
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* === SIDEBAR === */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLORS['primary']} 0%, #1a1a1a 100%);
        border-right: 1px solid {COLORS['border']};
    }}

    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown li,
    [data-testid="stSidebar"] label {{
        color: {COLORS['accent_light']} !important;
        font-family: {FONTS['body']};
    }}

    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {{
        color: {COLORS['accent']} !important;
        font-family: {FONTS['heading']};
    }}

    [data-testid="stSidebar"] hr {{
        border-color: rgba(200, 169, 110, 0.2);
    }}

    /* Sidebar radio buttons - force all text visible */
    [data-testid="stSidebar"] .stRadio > div {{
        gap: 2px;
    }}

    [data-testid="stSidebar"] .stRadio > div > label,
    [data-testid="stSidebar"] .stRadio > div > label p,
    [data-testid="stSidebar"] .stRadio > div > label span,
    [data-testid="stSidebar"] .stRadio > div > label div,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stRadio label p,
    [data-testid="stSidebar"] .stRadio label span {{
        color: {COLORS['accent_light']} !important;
        font-size: 0.9rem;
        font-weight: 400;
    }}

    [data-testid="stSidebar"] .stRadio > div > label {{
        background: transparent;
        border: none;
        border-radius: 8px;
        padding: 10px 16px;
        margin: 1px 0;
        transition: all 0.2s ease;
    }}

    [data-testid="stSidebar"] .stRadio > div > label:hover,
    [data-testid="stSidebar"] .stRadio > div > label:hover p,
    [data-testid="stSidebar"] .stRadio > div > label:hover span {{
        background: rgba(200, 169, 110, 0.15);
        color: {COLORS['accent']} !important;
    }}

    [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"],
    [data-testid="stSidebar"] .stRadio > div > label[aria-checked="true"] {{
        background: rgba(200, 169, 110, 0.2);
        border-left: 3px solid {COLORS['accent']};
    }}

    [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] p,
    [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] span,
    [data-testid="stSidebar"] .stRadio > div > label[aria-checked="true"] p,
    [data-testid="stSidebar"] .stRadio > div > label[aria-checked="true"] span {{
        color: {COLORS['accent']} !important;
        font-weight: 600;
    }}

    /* Sidebar caption */
    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] .stCaption p {{
        color: rgba(200, 169, 110, 0.4) !important;
    }}

    /* === MAIN CONTENT === */
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }}

    /* === HEADINGS === */
    .stMarkdown h1, .stMarkdown h2 {{
        font-family: {FONTS['heading']};
        color: {COLORS['primary']};
        font-weight: 600;
        letter-spacing: -0.02em;
    }}

    .stMarkdown h3, .stMarkdown h4 {{
        font-family: {FONTS['heading']};
        color: {COLORS['primary_light']};
        font-weight: 500;
    }}

    .stMarkdown p, .stMarkdown li {{
        font-family: {FONTS['body']};
        color: {COLORS['text']};
    }}

    /* === METRIC CARDS === */
    [data-testid="stMetric"] {{
        background: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 20px 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: all 0.2s ease;
    }}

    [data-testid="stMetric"]:hover {{
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-color: {COLORS['accent_light']};
    }}

    [data-testid="stMetric"] label {{
        font-family: {FONTS['body']};
        color: {COLORS['text_secondary']} !important;
        font-size: 0.78rem !important;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    [data-testid="stMetric"] [data-testid="stMetricValue"] {{
        font-family: {FONTS['heading']};
        color: {COLORS['primary']} !important;
        font-weight: 600;
        font-size: 1.5rem !important;
    }}

    /* === DATAFRAMES / TABLES === */
    [data-testid="stDataFrame"] {{
        border: 1px solid {COLORS['border']};
        border-radius: 10px;
        overflow: hidden;
    }}

    /* === FORMS & INPUTS === */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {{
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        font-family: {FONTS['body']};
        background: {COLORS['surface']};
        transition: border-color 0.2s ease;
    }}

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {COLORS['accent']};
        box-shadow: 0 0 0 2px rgba(200, 169, 110, 0.15);
    }}

    .stSelectbox > div > div {{
        border-radius: 8px;
    }}

    /* Labels */
    .stTextInput label, .stNumberInput label,
    .stSelectbox label, .stDateInput label,
    .stTextArea label, .stRadio label,
    .stFileUploader label {{
        font-family: {FONTS['body']};
        font-weight: 500;
        color: {COLORS['text']} !important;
        font-size: 0.85rem;
    }}

    /* === BUTTONS === */
    .stButton > button {{
        font-family: {FONTS['body']};
        font-weight: 500;
        border-radius: 8px;
        transition: all 0.2s ease;
        letter-spacing: 0.02em;
    }}

    .stButton > button[kind="primary"],
    .stFormSubmitButton > button {{
        background: {COLORS['accent']} !important;
        border: none !important;
        color: white !important;
        font-weight: 600;
        padding: 8px 24px;
    }}

    .stFormSubmitButton > button:hover,
    .stButton > button[kind="primary"]:hover {{
        background: {COLORS['accent_dark']} !important;
        box-shadow: 0 4px 12px rgba(200, 169, 110, 0.3);
    }}

    /* Secondary buttons */
    .stButton > button:not([kind="primary"]) {{
        border: 1px solid {COLORS['border']} !important;
        color: {COLORS['text']} !important;
    }}

    .stButton > button:not([kind="primary"]):hover {{
        border-color: {COLORS['accent']} !important;
        color: {COLORS['accent']} !important;
    }}

    /* Download buttons */
    .stDownloadButton > button {{
        font-family: {FONTS['body']};
        border: 1px solid {COLORS['border']} !important;
        border-radius: 8px;
        color: {COLORS['text']} !important;
        background: {COLORS['surface']} !important;
    }}

    .stDownloadButton > button:hover {{
        border-color: {COLORS['accent']} !important;
        color: {COLORS['accent']} !important;
    }}

    /* === EXPANDERS === */
    .streamlit-expanderHeader {{
        font-family: {FONTS['body']};
        font-weight: 600;
        color: {COLORS['primary']};
        background: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 10px;
    }}

    .streamlit-expanderContent {{
        border: 1px solid {COLORS['border']};
        border-top: none;
        border-radius: 0 0 10px 10px;
        background: {COLORS['surface']};
    }}

    /* === TABS === */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0;
        border-bottom: 2px solid {COLORS['border']};
    }}

    .stTabs [data-baseweb="tab"] {{
        font-family: {FONTS['body']};
        font-weight: 500;
        color: {COLORS['text_secondary']};
        border-bottom: 2px solid transparent;
        padding: 10px 20px;
    }}

    .stTabs [data-baseweb="tab"]:hover {{
        color: {COLORS['accent']};
    }}

    .stTabs [aria-selected="true"] {{
        color: {COLORS['accent']} !important;
        border-bottom-color: {COLORS['accent']} !important;
        font-weight: 600;
    }}

    /* === DIVIDERS === */
    .stMarkdown hr {{
        border-color: {COLORS['border_light']};
        margin: 1.5rem 0;
    }}

    /* === ALERTS === */
    .stAlert {{
        border-radius: 10px;
        font-family: {FONTS['body']};
    }}

    /* Success */
    [data-testid="stNotification"][data-type="success"] {{
        background-color: rgba(91, 140, 90, 0.08);
        border-left: 4px solid {COLORS['success']};
    }}

    /* Info */
    [data-testid="stNotification"][data-type="info"] {{
        background-color: rgba(107, 142, 174, 0.08);
        border-left: 4px solid {COLORS['info']};
    }}

    /* Warning */
    [data-testid="stNotification"][data-type="warning"] {{
        background-color: rgba(212, 168, 67, 0.08);
        border-left: 4px solid {COLORS['warning']};
    }}

    /* === FILE UPLOADER === */
    [data-testid="stFileUploader"] {{
        border: 2px dashed {COLORS['border']};
        border-radius: 10px;
        padding: 10px;
        background: {COLORS['surface']};
    }}

    [data-testid="stFileUploader"]:hover {{
        border-color: {COLORS['accent_light']};
    }}

    /* === RADIO (horizontal) === */
    .stRadio > div[role="radiogroup"] {{
        gap: 4px;
    }}

    /* === CAPTION === */
    .stCaption {{
        font-family: {FONTS['body']};
        color: {COLORS['text_light']};
    }}

    /* === CUSTOM CLASSES === */
    .page-header {{
        font-family: {FONTS['heading']};
        font-size: 1.8rem;
        font-weight: 600;
        color: {COLORS['primary']};
        margin-bottom: 0.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid {COLORS['accent']};
        display: inline-block;
    }}

    .section-header {{
        font-family: {FONTS['heading']};
        font-size: 1.1rem;
        font-weight: 500;
        color: {COLORS['primary_light']};
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 1rem;
    }}

    .brand-badge {{
        display: inline-block;
        background: {COLORS['accent']};
        color: white;
        padding: 2px 10px;
        border-radius: 12px;
        font-family: {FONTS['body']};
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }}

    .stat-label {{
        font-family: {FONTS['body']};
        font-size: 0.75rem;
        color: {COLORS['text_secondary']};
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 500;
    }}

    .stat-value {{
        font-family: {FONTS['heading']};
        font-size: 1.8rem;
        color: {COLORS['primary']};
        font-weight: 600;
    }}

    /* Scrollbar */
    ::-webkit-scrollbar {{
        width: 6px;
        height: 6px;
    }}
    ::-webkit-scrollbar-track {{
        background: {COLORS['background']};
    }}
    ::-webkit-scrollbar-thumb {{
        background: {COLORS['border']};
        border-radius: 3px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: {COLORS['accent_light']};
    }}
</style>
"""


def page_header(title, subtitle=None):
    """Render a styled page header."""
    import streamlit as st
    st.markdown(f'<div class="page-header">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<p style="color: {COLORS["text_secondary"]}; font-family: {FONTS["body"]}; margin-top: -4px;">{subtitle}</p>', unsafe_allow_html=True)


def section_header(title):
    """Render a styled section header."""
    import streamlit as st
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
