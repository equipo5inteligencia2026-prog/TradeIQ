import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from styles import render_interface, PLOTLY_CONFIG
from streamlit_autorefresh import st_autorefresh

# 1. CONFIGURACIÓN
st.set_page_config(layout="wide", initial_sidebar_state="expanded")
st_autorefresh(interval=10000, key="datarefresh")

render_interface("Dashboard")

# 2. FILTROS 
c_f1, c_f2 = st.columns([1, 1])
with c_f1:
    selected_ticker = st.selectbox("ACTIVO", ["FSM", "VOLCABC1", "BVN", "ABX", "SCCO"], index=0)
with c_f2:
    time_range = st.select_slider("RANGO", options=["1mo", "3mo", "1y"], value="1mo")
st.markdown('</div>', unsafe_allow_html=True)

# 3. FUNCIÓN DE DATOS
@st.cache_data(ttl=60)
def get_data_safely(ticker, period, is_watchlist=False):
    try:
        # 1. Descarga de datos
        df = yf.download(ticker, period=period, interval="1d", progress=False)
        
        if df is None or df.empty:
            return None

        # 2. Limpieza de MultiIndex
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # 3. Obtener precio actual REAL para inyectar en la última vela
        if not is_watchlist:
            try:
                t_obj = yf.Ticker(ticker)
                current_p = t_obj.fast_info.last_price
                if current_p:
                    df.loc[df.index[-1], 'Close'] = current_p
            except:
                pass
            
        return df
    except Exception as e:
        return None

# Activo principal (is_watchlist=False para que traiga el precio live)
df_main = get_data_safely(selected_ticker, time_range, is_watchlist=False)
# S&P 500
df_sp500 = get_data_safely("^GSPC", "5d", is_watchlist=True)

# 4. KPIs (Actualizados para leer por NOMBRE de columna, no por posición)
try:
    p_now = float(df_main['Close'].iloc[-1])
    p_prev = float(df_main['Close'].iloc[-2])
    p_change = ((p_now / p_prev) - 1) * 100
    
    sp_now = float(df_sp500['Close'].iloc[-1])
    sp_prev = float(df_sp500['Close'].iloc[-2])
    sp_pct = ((sp_now / sp_prev) - 1) * 100

    st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi">
            <div class="kpi-label">S&P 500 INDEX</div>
            <div class="kpi-val">{sp_now:,.2f}</div>
            <div class="kpi-change {'up' if sp_pct >= 0 else 'dn'}">{sp_pct:+.2f}%</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">{selected_ticker} PRICE</div>
            <div class="kpi-val">${p_now:,.2f}</div>
            <div class="kpi-change {'up' if p_change >= 0 else 'dn'}">{p_change:+.2f}%</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">MARKET STATUS</div>
            <div class="kpi-val">ACTIVE</div>
            <div class="kpi-change nu">LIVE STREAM</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">AI SENTIMENT</div>
            <div class="kpi-val">{'BUY' if p_change > 0 else 'HOLD'}</div>
            <div class="kpi-change up">REFRESCO: 10S</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
except:
    st.info("Sincronizando flujo de datos...")

# 5. CUERPO (GRÁFICO Y TABLA)
col_left, col_right = st.columns([1.6, 1], gap="large")

with col_left:
    st.markdown(f'<div class="card"><div class="card-title">ANÁLISIS TÉCNICO <span class="card-badge">{selected_ticker}</span></div>', unsafe_allow_html=True)
    if df_main is not None:
        fig = go.Figure(data=[go.Candlestick(x=df_main.index, open=df_main.iloc[:,0], high=df_main.iloc[:,1],
                                            low=df_main.iloc[:,2], close=df_main.iloc[:,3],
                                            increasing_line_color='#00e676', decreasing_line_color='#ff4444')])
        fig.update_layout(**PLOTLY_CONFIG)
        fig.update_layout(xaxis_rangeslider_visible=False, height=450)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    filas_html = ""
    for t in ["FSM", "VOLCABC1", "BVN", "ABX", "SCCO"]:
        # Pasamos is_watchlist=True para que la función cree una entrada de caché distinta
        d_temp = get_data_safely(t, "5d", is_watchlist=True)
        if d_temp is not None and not d_temp.empty:
            v_n = float(d_temp['Close'].iloc[-1])
            v_p = float(d_temp['Close'].iloc[-2])
            dif = ((v_n / v_p) - 1) * 100
            filas_html += f'<tr><td><b>{t}</b></td><td>${v_n:,.2f}</td><td class="{"up" if dif>=0 else "dn"}">{dif:+.2f}%</td></tr>'

    st.markdown(f"""
    <div class="card">
        <div class="card-title">WATCHLIST <span class="card-badge">LIVE</span></div>
        <table class="tbl">
            <thead><tr><th>TICKER</th><th>PRICE</th><th>CHG</th></tr></thead>
            <tbody>{filas_html}</tbody>
        </table>
    </div>
    <div class="card">
        <div class="card-title">IA SIGNALS</div>
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-family:'Space Mono'; font-size:12px;">PREDICTION MODEL</span>
            <span class="signal buy">BULLISH</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Cerramos el div "page" que se abre en styles.py
st.markdown('</div>', unsafe_allow_html=True)