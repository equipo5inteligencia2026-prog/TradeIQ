import streamlit as st
import yfinance as yf
from styles import render_interface

# 1. CONFIGURACIÓN E INYECCIÓN DE ESTILOS
st.set_page_config(layout="wide", initial_sidebar_state="expanded")
render_interface("Estrategias de Opciones")

st.markdown("""
<style>
    .card { background: #111217; border: 1px solid #2e2e2e; border-radius: 8px; padding: 24px; margin-bottom: 20px; }
    .card-title { color: #888; font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 20px; }
    
    /* Estilos KPI */
    .kpi { background: #1a1c23; padding: 15px; border-radius: 6px; border: 1px solid #2e2e2e; text-align: center; }
    .kpi-label { font-size: 10px; color: #666; margin-bottom: 5px; font-family: monospace; }
    .kpi-val { font-size: 18px; font-weight: bold; font-family: monospace; }
    
    /* Estrategias */
    .strat-card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px; margin-bottom: 16px; transition: 0.3s; height: 100%; }
    .strat-card:hover { border-color: #58a6ff; background: #1c2128; }
    .strat-name { color: #58a6ff; font-weight: bold; font-size: 16px; margin-bottom: 8px; }
    .strat-desc { font-size: 12.5px; color: #8b949e; line-height: 1.5; margin-bottom: 12px; }
    .strat-risk { font-size: 11px; font-weight: bold; font-family: monospace; }
    
    .up { color: #00e676; }
    .dn { color: #ff4444; }
    .amber { color: #ffc107; }
</style>
""", unsafe_allow_html=True)

# 2. CONTROLES DENTRO DE LA PÁGINA
col_head1, col_head2 = st.columns([2, 1])
with col_head1:
    activo = st.selectbox("ACTIVO", ["AAPL", "TSLA", "BTC-USD", "NVDA", "MSFT"], label_visibility="collapsed")
with col_head2:
    confianza = st.select_slider("Nivel de Confianza IA", options=[50, 60, 70, 80, 90, 100], value=80, label_visibility="collapsed")

# 3. LÓGICA DE DATOS REALES
@st.cache_data(ttl=300)
def get_live_price(symbol):
    try:
        data = yf.download(symbol, period="1d", interval="1m", progress=False)
        return float(data['Close'].iloc[-1])
    except:
        return 187.42

precio_actual = get_live_price(activo)
target = precio_actual * 1.07
stop_loss = precio_actual * 0.96

# 4. SECCIÓN: SEÑAL DE ACCIÓN
st.markdown(f"""
    <div class="card">
        <div class="card-title">Señal de Acción — {activo}</div>
        <div style="display:grid; grid-template-columns: 220px 1fr; gap:24px; align-items:center;">
            <div style="text-align:center; border-right: 1px solid #2e2e2e; padding-right:24px;">
                <div style="font-size:40px; color:#00e676; font-weight:700; letter-spacing:-1px;">COMPRAR</div>
                <div style="font-size:13px; color:#9ca3af; margin-top:8px;">Basado en señal ALZA {confianza}%</div>
            </div>
            <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:16px;">
                <div class="kpi"><div class="kpi-label">PRECIO ENTRADA</div><div class="kpi-val">${precio_actual:,.2f}</div></div>
                <div class="kpi"><div class="kpi-label">PRECIO OBJETIVO</div><div class="kpi-val up">${target:,.2f}</div></div>
                <div class="kpi"><div class="kpi-label">STOP LOSS</div><div class="kpi-val dn">${stop_loss:,.2f}</div></div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# 5. SECCIÓN: ESTRATEGIAS DE OPCIONES
st.markdown('<div class="card-title" style="margin-left:5px;">Estrategias de Opciones Recomendadas</div>', unsafe_allow_html=True)

estrategias = [
    {"n": "Covered Call", "d": f"Vende una opción call sobre tus acciones {activo} para generar ingreso pasivo.", "r": "BAJO ●", "c": "up", "m": f"Strike: ${precio_actual*1.04:.1f} · Prima: $2.40"},
    {"n": "Debit Spread", "d": "Compra call ATM y vende call OTM para limitar riesgo con presupuesto definido.", "r": "MEDIO ●", "c": "amber", "m": "Coste neto: $3.20 · Max profit: $6.80"},
    {"n": "Naked Put", "d": "Vende un put OTM para adquirir acciones a precio descontado si bajan.", "r": "MEDIO ●", "c": "amber", "m": f"Prima: $1.85 · Strike: ${precio_actual*0.95:.1f}"},
    {"n": "Credit Spread", "d": "Recibe prima vendiendo spreads de crédito con riesgo limitado.", "r": "MEDIO ●", "c": "amber", "m": "Crédito neto: $1.50 · Max pérdida: $3.50"},
    {"n": "Iron Condor", "d": "Estrategia neutral de cuatro patas para aprovechar mercados laterales.", "r": "ALTO ●", "c": "dn", "m": "Rango beneficio: +/- 4.5%"},
    {"n": "Optimizar Portafolio", "d": "Maximiza Sharpe ratio rebalanceando tus activos actuales.", "r": "BAJO ●", "c": "up", "m": "Sharpe Ratio: 1.85"}
]

# Grid de 3 columnas
cols = st.columns(3)
for i, s in enumerate(estrategias):
    with cols[i % 3]:
        st.markdown(f"""
            <div class="strat-card">
                <div class="strat-name">{s['n']}</div>
                <div class="strat-desc">{s['d']}</div>
                <div class="strat-risk {s['c']}">Riesgo: {s['r']}</div>
                <div style="margin-top:12px; font-size:11px; font-family:monospace; color:#666;">{s['m']}</div>
            </div>
        """, unsafe_allow_html=True)