import streamlit as st
import pandas as pd
import logging
import uuid
from datetime import datetime
from database.connection import get_session
from database.models import User, Portfolio
from database.init_db import init_database, hash_password

logging.basicConfig(level=logging.INFO)

# ============================================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================================
st.set_page_config(
    page_title="TradeIQ — Predicción Bursátil con IA",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

LOGIN_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
<style>
    :root {
        --bg: #f4f6f9; --panel: #ffffff; --panel2: #f0f3f7;
        --border: #dde3ec; --border2: #c8d2de;
        --cyan: #0077cc; --green: #00a854; --red: #e03131;
        --text: #6b7a8d; --white: #1a2535;
        --font: 'Syne', sans-serif; --mono: 'Space Mono', monospace;
    }

    /* 1. Resetear Streamlit a pantalla completa */
    html, body, [class*="st-"] { font-family: var(--font); }
    .stApp { background: var(--bg) !important; overflow: hidden !important; }
    [data-testid="stHeader"] { display: none !important; }
    .main .block-container { padding: 0 !important; max-width: 100% !important; }

    /* 2. Forzar altura de columnas a 100vh (Layout de pantalla dividida) */
    [data-testid="stHorizontalBlock"] { height: 100vh; gap: 0 !important; align-items: stretch; }

    /* Lado Izquierdo (Panel claro con gradientes suaves) */
    [data-testid="column"]:nth-child(1) {
        background: var(--panel) !important;
        border-right: 1px solid var(--border) !important;
        padding: 80px !important;
        display: flex !important; flex-direction: column !important; justify-content: center !important;
        position: relative; overflow: hidden;
        box-shadow: 2px 0 12px rgba(0,0,0,0.04);
    }
    /* Efectos de luz suaves para tema claro */
    [data-testid="column"]:nth-child(1)::before {
        content: ''; position: absolute; top: -100px; left: -100px; width: 500px; height: 500px;
        background: radial-gradient(circle, rgba(0,119,204,0.06) 0%, transparent 70%); pointer-events: none;
    }
    [data-testid="column"]:nth-child(1)::after {
        content: ''; position: absolute; bottom: -100px; right: -50px; width: 400px; height: 400px;
        background: radial-gradient(circle, rgba(0,168,84,0.05) 0%, transparent 70%); pointer-events: none;
    }

    /* Lado Derecho (Formulario) */
    [data-testid="column"]:nth-child(2) {
        background: var(--bg) !important;
        padding: 80px 60px !important;
        display: flex !important; flex-direction: column !important; justify-content: center !important;
    }

    /* 3. Textos del lado izquierdo */
    .login-brand { font-size: 13px; font-family: var(--mono); color: var(--cyan); letter-spacing: 3px; margin-bottom: 48px; position: relative; z-index: 1; }
    .login-headline { font-size: 52px; font-weight: 800; line-height: 1.05; color: var(--white); margin-bottom: 20px; position: relative; z-index: 1; }
    .login-headline span { color: var(--cyan); }
    .login-sub { font-size: 15px; color: var(--text); line-height: 1.7; max-width: 380px; position: relative; z-index: 1; }
    .login-stats { display: flex; gap: 40px; margin-top: 60px; position: relative; z-index: 1; }
    .ls { display: flex; flex-direction: column; }
    .ls-val { font-size: 28px; font-weight: 700; color: var(--cyan); }
    .ls-lbl { font-size: 11px; font-family: var(--mono); color: var(--text); letter-spacing: 1px; margin-top: 2px; }

    /* 4. Pestañas de Streamlit */
    [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid var(--border) !important; gap: 0 !important; margin-bottom: 30px !important; }
    [data-baseweb="tab"] {
        flex: 1 !important; text-align: center !important; padding: 14px !important;
        font-size: 13px !important; font-weight: 600 !important; color: var(--text) !important;
        background: transparent !important; border: none !important; border-bottom: 2px solid transparent !important;
    }
    [data-baseweb="tab"][aria-selected="true"] { color: var(--cyan) !important; border-bottom-color: var(--cyan) !important; }

    /* 5. Inputs y Selects */
    .stTextInput label p, .stSelectbox label p {
        font-size: 12px !important; font-family: var(--mono) !important;
        color: var(--text) !important; letter-spacing: 1px !important; text-transform: uppercase;
    }
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background: var(--panel) !important; border: 1px solid var(--border2) !important;
        border-radius: 4px !important; padding: 14px 16px !important;
        font-size: 14px !important; color: var(--white) !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
    }
    .stTextInput input:focus, .stSelectbox div[data-baseweb="select"]:focus-within {
        border-color: var(--cyan) !important;
        box-shadow: 0 0 0 3px rgba(0,119,204,0.1) !important;
    }
    .stTextInput input::placeholder { color: var(--border2) !important; }

    /* 6. Botón Primary */
    button[kind="primary"] {
        background: var(--cyan) !important; color: #fff !important; border: none !important;
        padding: 24px 16px !important; font-size: 14px !important; font-weight: 700 !important;
        border-radius: 4px !important; letter-spacing: 1px !important; margin-top: 10px !important;
        transition: 0.2s !important; width: 100% !important;
        box-shadow: 0 2px 8px rgba(0,119,204,0.25) !important;
    }
    button[kind="primary"]:hover { opacity: 0.9 !important; transform: translateY(-1px) !important; }
    button[kind="primary"] p { font-size: 14px !important; font-weight: 700 !important; }

    /* 7. Mensajes de error/éxito */
    [data-testid="stAlert"] {
        border-radius: 4px !important;
        font-size: 13px !important;
    }
</style>
"""

st.markdown(LOGIN_CSS, unsafe_allow_html=True)

# ============================================================================
# LÓGICA DE BASE DE DATOS Y ESTADO
# ============================================================================
init_database()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None

# Si ya está logueado, enviar directo al Dashboard interno
if st.session_state.logged_in:
    st.switch_page("pages/1_Dashboard.py")

# ============================================================================
# INTERFAZ DE LOGIN
# ============================================================================
col_left, col_right = st.columns([1.5, 1])

# Diseño y Branding
with col_left:
    st.markdown("""
    <div class="login-brand">// TRADEIQ · SISTEMA DE PREDICCIÓN BURSÁTIL</div>
    <div class="login-headline">Decisiones de inversión<br>potenciadas por <span>IA</span></div>
    <div class="login-sub">12 modelos de Machine Learning y Deep Learning analizan el mercado en tiempo real para darte las mejores señales de trading.</div>
    <div class="login-stats">
        <div class="ls"><span class="ls-val">12</span><span class="ls-lbl">MODELOS IA</span></div>
        <div class="ls"><span class="ls-val">78%</span><span class="ls-lbl">PRECISIÓN</span></div>
        <div class="ls"><span class="ls-val">30D</span><span class="ls-lbl">HORIZONTE</span></div>
    </div>
    """, unsafe_allow_html=True)

# Formulario de Autenticación
with col_right:
    st.markdown("<div style='max-width: 480px; margin: 0 auto; width: 100%;'>", unsafe_allow_html=True)

    t1, t2 = st.tabs(["Iniciar Sesión", "Registrarse"])

    # TAB 1: LOGIN
    with t1:
        email = st.text_input("Correo Electrónico", placeholder="trader@tradeiq.com", value="trader@tradeiq.com", key="l_email")
        password = st.text_input("Contraseña", type="password", placeholder="••••••••", value="password123", key="l_pass")

        if st.button("INGRESAR AL SISTEMA", use_container_width=True, type="primary"):
            if email and password:
                session = get_session()
                try:
                    user = session.query(User).filter(User.email == email).first()
                    if user and user.password_hash == hash_password(password):
                        st.session_state.logged_in = True
                        st.session_state.user_id = user.user_id
                        st.session_state.user_email = user.email
                        st.rerun()
                    else:
                        st.error("❌ Credenciales inválidas. Verifica tus datos.")
                finally:
                    session.close()
            else:
                st.error("❌ Por favor completa todos los campos.")

        st.markdown("""
        <div style='font-size: 12px; text-align: center; color: var(--text); margin-top: 16px;'>
            <a href='#' style='color: var(--cyan); text-decoration: none;'>¿Olvidaste tu contraseña?</a>
        </div>
        """, unsafe_allow_html=True)

    # TAB 2: REGISTRO
    with t2:
        r_name = st.text_input("Nombre Completo", placeholder="Ana García", key="r_name")
        r_email = st.text_input("Correo Electrónico", placeholder="tu@correo.com", key="r_email")
        r_pass = st.text_input("Contraseña", type="password", placeholder="Mínimo 8 caracteres", key="r_pass")
        r_risk = st.selectbox("Perfil de Riesgo", ["Conservador", "Moderado", "Agresivo"], index=1, key="r_risk")

        if st.button("CREAR CUENTA", use_container_width=True, type="primary"):
            if r_name and r_email and r_pass:
                session = get_session()
                try:
                    if session.query(User).filter(User.email == r_email).first():
                        st.error("❌ Este correo ya está registrado.")
                    else:
                        new_id = str(uuid.uuid4())
                        new_user = User(
                            user_id=new_id,
                            email=r_email,
                            username=r_email.split("@")[0],
                            password_hash=hash_password(r_pass),
                            name=r_name,
                            risk_profile=r_risk.lower(),
                            created_at=datetime.utcnow()
                        )
                        portfolio = Portfolio(
                            portfolio_id=str(uuid.uuid4()),
                            user_id=new_id,
                            name="Mi Portafolio",
                            total_value=10000.0,
                            cash_available=10000.0,
                            created_at=datetime.utcnow()
                        )
                        session.add(new_user)
                        session.add(portfolio)
                        session.commit()
                        st.success("✅ Cuenta creada exitosamente. Ya puedes iniciar sesión.")
                finally:
                    session.close()
            else:
                st.error("❌ Completa todos los campos.")

    st.markdown("</div>", unsafe_allow_html=True)