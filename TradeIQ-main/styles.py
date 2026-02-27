import streamlit as st
from datetime import datetime

LIGHT_THEME = """
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
<style>
    :root {
        --bg: #f4f6f9; --panel: #ffffff; --panel2: #f0f3f7;
        --border: #dde3ec; --border2: #c8d2de;
        --cyan: #0077cc; --green: #00a854; --red: #e03131;
        --amber: #e67700; --text: #6b7a8d; --white: #1a2535;
        --font: 'Syne', sans-serif; --mono: 'Space Mono', monospace;
    }

    /* Fondo general de Streamlit */
    .stApp {
        background: var(--bg) !important;
    }

    [data-testid="stSidebar"] {
        background: var(--panel) !important;
        border-right: 1px solid var(--border) !important;
    }

    [data-testid="stSidebarNav"] { display: none !important; }

    [data-testid="stSidebarUserContent"] { padding-top: 0rem !important; }

    [data-testid="collapsedControl"] {
        display: flex !important;
        background: var(--panel) !important;
        color: var(--cyan) !important;
    }

    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }

    [data-testid="stAppViewBlockContainer"] {
        padding: 0px !important;
    }

    [data-testid="stSidebar"] {
        background: var(--panel) !important;
        border-right: 1px solid var(--border) !important;
        min-width: 220px !important; max-width: 220px !important;
    }
    [data-testid="stSidebarUserContent"] { padding: 0 !important; }

    div[data-testid="stSidebar"] button {
        display: flex !important; align-items: center !important; gap: 12px !important;
        padding: 11px 24px !important; font-size: 13px !important; font-weight: 600 !important;
        color: var(--text) !important; background: transparent !important;
        border: none !important; border-left: 3px solid transparent !important;
        border-radius: 0 !important; width: 100% !important; text-align: left !important;
        box-shadow: none !important; margin: 0 !important;
    }
    div[data-testid="stSidebar"] button:hover {
        color: var(--white) !important; background: rgba(0,0,0,0.04) !important;
    }
    div[data-testid="stSidebar"] button[kind="primary"] {
        color: var(--cyan) !important; background: rgba(0,119,204,0.07) !important;
        border-left-color: var(--cyan) !important;
    }

    /* Etiquetas de sección en sidebar */
    .sb-section-label {
        font-family: var(--mono);
        font-size: 9px;
        letter-spacing: 1.5px;
        color: var(--text);
        opacity: 0.6;
        padding: 16px 24px 6px;
    }
    
    [data-testid="stWidgetLabel"] p {
        color: #1a2535 !important;
    }

    .topbar {
        position: sticky; top: 0; z-index: 10; background: var(--panel);
        border-bottom: 1px solid var(--border); display: flex; align-items: center;
        justify-content: space-between; padding: 0 24px; height: 56px;
        width: 100%; margin: 0; box-sizing: border-box;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .topbar-title { font-size: 15px; font-weight: 700; color: var(--white); font-family: var(--font); }
    .topbar-right { display: flex; align-items: center; gap: 16px; }
    .live-dot { width: 8px; height: 8px; background: var(--green); border-radius: 50%; animation: pulse 2s infinite; }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
    .live-label { font-size: 11px; font-family: var(--mono); color: var(--green); }

    .page {
        padding: 24px 15px;
        width: 100%;
        box-sizing: border-box;
        background: var(--bg);
        
    }

    /* KPIs */
    .kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 28px; }
    .kpi {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 20px 24px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    .kpi-label { font-size: 11px; font-family: var(--mono); color: var(--text); letter-spacing: 1px; margin-bottom: 8px; }
    .kpi-val { font-size: 26px; font-weight: 700; color: var(--white); font-family: var(--font); }
    .kpi-change { font-size: 12px; margin-top: 4px; }
    .up { color: var(--green) !important; font-weight: 600; }
    .dn { color: var(--red) !important; font-weight: 600; }
    .nu { color: var(--cyan) !important; }

    /* CARDS & TABLES */
    .card {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    .card-title {
        font-size: 13px; font-weight: 700; color: var(--white);
        margin-bottom: 20px; display: flex; align-items: center;
        justify-content: space-between; text-transform: uppercase;
        font-family: var(--font);
    }
    .card-badge {
        font-size: 10px; font-family: var(--mono); padding: 3px 10px;
        border-radius: 2px; background: rgba(0,119,204,0.08);
        color: var(--cyan); border: 1px solid rgba(0,119,204,0.2);
    }

    .tbl { width: 100%; border-collapse: collapse; font-size: 13px; }
    .tbl th {
        font-family: var(--mono); font-size: 10px; color: var(--text);
        letter-spacing: 1px; padding: 10px 12px;
        border-bottom: 1px solid var(--border); text-align: left;
    }
    .tbl td { padding: 12px 12px; border-bottom: 1px solid var(--border); color: var(--white); font-size: 13px; }
    .tbl tr:hover td { background: rgba(0,0,0,0.02); }

    /* SIGNALS */
    .signal { display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 2px; font-size: 11px; font-family: var(--mono); font-weight: 700; }
    .signal.buy  { background: rgba(0,168,84,0.10);  color: var(--green); border: 1px solid rgba(0,168,84,0.25); }
    .signal.sell { background: rgba(224,49,49,0.10); color: var(--red);   border: 1px solid rgba(224,49,49,0.25); }
    .signal.hold { background: rgba(230,119,0,0.10); color: var(--amber); border: 1px solid rgba(230,119,0,0.25); }
</style>
"""

PLOTLY_CONFIG = dict(
    template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#6b7a8d", family="Space Mono", size=10), margin=dict(l=0, r=0, t=10, b=0),
    xaxis=dict(gridcolor="#dde3ec", showgrid=True), yaxis=dict(gridcolor="#dde3ec", showgrid=True)
)

def render_interface(page_title):
    st.markdown(LIGHT_THEME, unsafe_allow_html=True)

    with st.sidebar:
        # BRANDING
        st.markdown(f"""
        <div style="padding: 32px 24px 20px;">
            <div style="font-size: 20px; font-weight: 800; color: var(--cyan); letter-spacing: -1px; font-family: var(--font);">TradeIQ</div>
            <div style="font-size: 11px; font-family: var(--mono); color: var(--text); margin-top: 4px; opacity: 0.7;">trader@tradeiq.com</div>
        </div>
        """, unsafe_allow_html=True)

        # --- SECCIÓN: MERCADO ---
        st.markdown('<div class="sb-section-label">MERCADO</div>', unsafe_allow_html=True)
        nav_items = {
            "Dashboard": ("⊞", "pages/1_Dashboard.py"),
            "Acciones": ("📈", "pages/2_Acciones.py"),
            "Criptomonedas": ("₿", "pages/3_Cripto.py"),
        }
        for name, (icon, path) in nav_items.items():
            if st.button(f"{icon} {name}", key=f"nav_{name}", use_container_width=True,
                         type="primary" if name == page_title else "secondary"):
                st.switch_page(path)

        # --- SECCIÓN: ANÁLISIS IA ---
        st.markdown('<div class="sb-section-label">ANÁLISIS IA</div>', unsafe_allow_html=True)
        ia_items = {
            "Predicciones": ("🤖", "pages/4_Predicciones.py"),
            "Noticias & NLP": ("📰", "pages/5_Noticias.py"),
        }
        for name, (icon, path) in ia_items.items():
            if st.button(f"{icon} {name}", key=f"nav_{name}", use_container_width=True,
                         type="primary" if name == page_title else "secondary"):
                st.switch_page(path)

        # --- SECCIÓN: TRADING ---
        st.markdown('<div class="sb-section-label">TRADING</div>', unsafe_allow_html=True)
        trading_items = {
            "Estrategias": ("🎯", "pages/6_Estrategias.py"),
            "Backtesting": ("🔄", "pages/7_Backtesting.py"),
            "Mi Portafolio": ("💼", "pages/8_Portafolio.py"),
            "Enviar Orden": ("📤", "pages/9_Ordenes.py"),
            "Alertas": ("🔔", "pages/10_Alertas.py"),
        }
        for name, (icon, path) in trading_items.items():
            if st.button(f"{icon} {name}", key=f"nav_{name}", use_container_width=True,
                         type="primary" if name == page_title else "secondary"):
                st.switch_page(path)

        # --- BOTTOM / LOGOUT ---
        st.markdown('<div style="margin-top: 20px; padding: 0 24px;"><hr style="border-color: var(--border); opacity:0.5;"></div>', unsafe_allow_html=True)
        if st.button("↩ Cerrar Sesión", use_container_width=True, key="logout_btn"):
            st.session_state.clear()
            st.switch_page("app.py")

    now = datetime.now().strftime("%H:%M:%S")
    layout_html = f"""
    <div class="topbar">
        <div class="topbar-title">{page_title.upper()}</div>
        <div class="topbar-right">
            <div class="live-dot"></div>
            <span class="live-label">MERCADO EN VIVO</span>
            <span style="font-family:var(--mono);font-size:12px;color:var(--text)">{now}</span>
        </div>
    </div>
    <div class="page active">
    """
    st.markdown(layout_html, unsafe_allow_html=True)