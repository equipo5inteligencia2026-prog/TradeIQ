import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import vectorbt as vbt  # Librería core para el cálculo
from styles import render_interface
import plotly.graph_objects as go

# 1. CONFIGURACIÓN E INYECCIÓN DE ESTILOS
st.set_page_config(layout="wide")
render_interface("Backtesting")

# (Mantenemos tu bloque de CSS original...)
st.markdown("""
<style>
    .card { background: #ffffff; border: 1px solid #dee2e6; border-radius: 8px; padding: 24px; margin-bottom: 20px; }
    .card-title { color: #000; font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 20px; }
    .metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }
    .metric-box { background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; border-radius: 6px; text-align: center; }
    .metric-lbl { font-size: 10px; color: #666; font-family: monospace; margin-bottom: 5px; }
    .metric-val { font-size: 18px; font-weight: bold; font-family: monospace; color: #000; }
    .up { color: #28a745; }
    .dn { color: #dc3545; }
    .nu { color: #6c757d; }
    label { font-size: 11px; font-family: monospace; color: #888; letter-spacing: 1px; display: block; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

# 2. FILTROS DE BACKTESTING ACTUALIZADOS
# Ajustamos las columnas para que quepa el Ticker
col_tkr, col_strat, col_per, col_cap, col_btns = st.columns([0.8, 1.5, 1, 1, 1.5], gap="small")

with col_tkr:
    st.markdown("<label>ACTIVO</label>", unsafe_allow_html=True)
    # Lista de empresas populares o puedes dejar que el usuario escriba
    symbol = st.selectbox("Ticker", ["FSM", "BHP", "BVN", "ABX", "SCCO", "BTC-USD"], index=0, label_visibility="collapsed")

with col_strat:
    st.markdown("<label>ESTRATEGIA IA</label>", unsafe_allow_html=True)
    estrategia = st.selectbox("Estrat", ["Tendencia LSTM", "Momentum GRU", "Reversión Media"], label_visibility="collapsed")

with col_per:
    st.markdown("<label>PERÍODO</label>", unsafe_allow_html=True)
    periodo = st.selectbox("Periodo", ["6 meses", "1 año", "2 años", "5 años"], index=1, label_visibility="collapsed")

with col_cap:
    st.markdown("<label>CAPITAL (USD)</label>", unsafe_allow_html=True)
    capital = st.number_input("Cap", value=10000, step=1000, label_visibility="collapsed")

with col_btns:
    st.markdown("<label>&nbsp;</label>", unsafe_allow_html=True)
    c_btn1, c_btn2 = st.columns(2)
    ejecutar = c_btn1.button("▶ SIMULAR", width="stretch", type="primary") # Usando el nuevo formato width

# 3. LÓGICA CON VECTORBT
if ejecutar:
    with st.spinner(f"Analizando histórico de {symbol}..."):
        p_map = {"6 meses": "6mo", "1 año": "1y", "2 años": "2y", "5 años": "5y"}
        
        # Descarga dinámica según el Ticker seleccionado
        data = yf.download(symbol, period=p_map[periodo], progress=False, auto_adjust=True)
        
        # IMPORTANTE: VectorBT necesita que 'close' sea una Serie de Pandas limpia
        if isinstance(data.columns, pd.MultiIndex):
            close = data['Close'][symbol]
        else:
            close = data['Close']

        # ESTRATEGIA: Cruce de Medias
        fast_ma = vbt.MA.run(close, 10)
        slow_ma = vbt.MA.run(close, 50)
        entries = fast_ma.ma_crossed_above(slow_ma)
        exits = fast_ma.ma_crossed_below(slow_ma)

        # 1. DEFINIR FRECUENCIA AL CREAR EL PORTAFOLIO
        pf = vbt.Portfolio.from_signals(
            close, entries, exits, 
            init_cash=capital, 
            fees=0.001, 
            freq='1D'  # <--- Esto quita los avisos de Sharpe/Sortino
        )
        
        # 2. SELECCIONAR SOLO UNA COLUMNA PARA EVITAR EL WARNING DE "MULTIPLE COLUMNS"
        # Si 'close' es un DataFrame, seleccionamos la primera serie
        stats = pf.stats()
        
        # 3. RENDER DE MÉTRICAS SEGURO (Convertimos a float explícitamente)
        st.markdown(f"""
            <div class="metric-grid">
                <div class="metric-box"><div class="metric-lbl">RETORNO TOTAL</div><div class="metric-val up">{float(stats.get('Total Return [%]', 0)):.2f}%</div></div>
                <div class="metric-box"><div class="metric-lbl">RATIO SHARPE</div><div class="metric-val up">{float(stats.get('Sharpe Ratio', 0)):.2f}</div></div>
                <div class="metric-box"><div class="metric-lbl">MAX DRAWDOWN</div><div class="metric-val dn">{float(stats.get('Max Drawdown [%]', 0)):.2f}%</div></div>
                <div class="metric-box"><div class="metric-lbl">WIN RATE</div><div class="metric-val up">{float(stats.get('Win Rate [%]', 0)):.1f}%</div></div>
                <div class="metric-box"><div class="metric-lbl">PROFIT FACTOR</div><div class="metric-val up">{float(stats.get('Profit Factor', 0)):.2f}</div></div>
                <div class="metric-box"><div class="metric-lbl">N° OPERACIONES</div><div class="metric-val nu">{int(stats.get('Total Trades', 0))}</div></div>
            </div>
        """, unsafe_allow_html=True)

        # 4. GRÁFICOS (Actualizando use_container_width por el nuevo formato si es necesario)
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown('<div class="card-title">Equity Curve</div>', unsafe_allow_html=True)
            fig_eq = pf.value().vbt.plot(trace_kwargs=dict(name='Equity', line=dict(color='#28a745')))
            fig_eq.update_layout(template="plotly_white", height=300, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_eq, width="stretch") # Actualizado

        with col_g2:
            st.markdown('<div class="card-title">Drawdown</div>', unsafe_allow_html=True)
            fig_dd = pf.drawdown().vbt.plot(trace_kwargs=dict(name='Drawdown', line=dict(color='#dc3545')))
            fig_dd.update_layout(template="plotly_white", height=300, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_dd, width="stretch") # Actualizado

        # 5. EL FIX PARA EL ERROR DE ARROW/DATAFRAME
        with st.expander("Ver Reporte Completo"):
            # Convertimos a string o a un DF simple para que no falle al serializar
            st.table(stats.astype(str))