import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from styles import render_interface
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

# 1. CONFIGURACIÓN Y REFRESCO
st.set_page_config(layout="wide", initial_sidebar_state="expanded")
st_autorefresh(interval=10000, key="crypto_refresh")
render_interface("Bitcoin & Cripto")

# 2. SELECTOR Y FILTROS
col_sel, col_btns = st.columns([1, 2])
with col_sel:
    crypto_choice = st.selectbox(
        "ACTIVO", 
        ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"], 
        index=0, 
        label_visibility="collapsed"
    )

# 3. DATA FETCHING
@st.cache_data(ttl=60)
def get_crypto_full_data(symbol):
    try:
        t = yf.Ticker(symbol)
        info = t.info
        hist = t.history(period="1mo")
        return info, hist
    except:
        return {}, None

info, hist = get_crypto_full_data(crypto_choice)
price = info.get('regularMarketPrice', info.get('currentPrice', 0))
change = info.get('regularMarketChangePercent', 0)

# 4. KPIs
st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi">
            <div class="kpi-label">PRECIO {crypto_choice.split('-')[0]}</div>
            <div class="kpi-val">${price:,.0f}</div>
            <div class="kpi-change {'up' if change >= 0 else 'dn'}">{'▲' if change >= 0 else '▼'} {change:+.2f}%</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">CAP. DE MERCADO</div>
            <div class="kpi-val">${info.get('marketCap', 0)/1e12:.2f}T</div>
            <div class="kpi-change nu">Global</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">VOLUMEN 24H</div>
            <div class="kpi-val">${info.get('totalVolume', 0)/1e9:.1f}B</div>
            <div class="kpi-change up">▲ Alto</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">DOMINANCIA</div>
            <div class="kpi-val">52.4%</div>
            <div class="kpi-change up">▲ BTC</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# 5. GRÁFICO PRINCIPAL
st.markdown(f'<div style="margin-bottom:5px; font-weight:bold; color:var(--white);">{crypto_choice.replace("-USD", " (USD)")} <span style="color:var(--amber);font-size:12px">⚠ Alta volatilidad</span></div>', unsafe_allow_html=True)

tv_symbol = f"BINANCE:{crypto_choice.replace('-USD', '')}USDT"
tv_widget = f"""
    <div style="width: 100%; height: 400px; border-radius: 4px; overflow: hidden; border: 1px solid var(--border2);">
        <div id="tv-crypto" style="height: 100%;"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
          new TradingView.widget({{
          "autosize": true, "symbol": "{tv_symbol}", "interval": "60",
          "timezone": "Etc/UTC", "theme": "dark", "style": "1",
          "locale": "es", "enable_publishing": false, "container_id": "tv-crypto"
        }});
        </script>
    </div>
"""
components.html(tv_widget, height=410)

# 6. GRID INFERIOR
st.markdown('<div class="grid-2">', unsafe_allow_html=True)

# Lógica de datos
tickers_table = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"]
rows_body = ""

for t in tickers_table:
    try:
        d_hist = yf.download(t, period="35d", interval="1d", progress=False)
        if isinstance(d_hist.columns, pd.MultiIndex): d_hist.columns = d_hist.columns.get_level_values(0)
        actual = d_hist['Close'].iloc[-1]
        c24h = ((actual / d_hist['Close'].iloc[-2]) - 1) * 100
        c7d = ((actual / d_hist['Close'].iloc[-7]) - 1) * 100
        c30d = ((actual / d_hist['Close'].iloc[0]) - 1) * 100
        
        rows_body += f"""
            <tr class="row-hover">
                <td style="padding: 15px; font-weight: 600; color: #fff;">{t.split('-')[0]}</td>
                <td class="{'up' if c24h >= 0 else 'dn'}" style="padding: 15px; text-align: center;">{c24h:+.2f}%</td>
                <td class="{'up' if c7d >= 0 else 'dn'}" style="padding: 15px; text-align: center;">{c7d:+.2f}%</td>
                <td class="{'up' if c30d >= 0 else 'dn'}" style="padding: 15px; text-align: center;">{c30d:+.2f}%</td>
            </tr>
        """
    except: continue

layout_final = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    body {{ font-family: 'Inter', sans-serif; background-color: transparent; }}
    
    .grid-custom {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 25px;
        margin-top: 10px;
    }}
    
    .card-full {{
        background: #0e1117;
        border: 1px solid #2e2e2e;
        border-radius: 12px;
        padding: 24px;
        height: 400px;
        display: flex;
        flex-direction: column;
        align-items: center; /* Centra el contenido horizontalmente */
    }}
    
    .title {{ 
        color: #9ca3af; 
        font-weight: 600; 
        margin-bottom: 20px; 
        font-size: 13px; 
        text-transform: uppercase; 
        letter-spacing: 1px;
        width: 100%;
        text-align: left;
    }}
    
    /* Estilo Mejorado de la Tabla */
    .modern-table {{
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        margin: auto; /* Centra la tabla si es más pequeña */
    }}
    
    .modern-table thead th {{
        color: #6b7280;
        font-size: 11px;
        text-align: center;
        padding: 10px;
        border-bottom: 1px solid #2e2e2e;
    }}
    
    .modern-table thead th:first-child {{ text-align: left; }}
    
    .row-hover:hover {{ background: #1f2937; transition: 0.3s; }}
    
    .up {{ color: #10b981; font-weight: 600; }}
    .dn {{ color: #ef4444; font-weight: 600; }}
    
    .chart-container {{
        width: 100%;
        height: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
    }}
</style>

<div class="grid-custom">
    <div class="card-full">
        <div class="title">Variación por período</div>
        <table class="modern-table">
            <thead>
                <tr>
                    <th style="text-align: left;">ACTIVO</th>
                    <th>24 HORAS</th>
                    <th>7 DÍAS</th>
                    <th>30 DÍAS</th>
                </tr>
            </thead>
            <tbody>
                {rows_body}
            </tbody>
        </table>
    </div>

    <div class="card-full">
        <div class="title">Dominancia del Mercado</div>
        <div class="chart-container">
            <canvas id="chartDom" style="max-width: 280px; max-height: 280px;"></canvas>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
    const ctx = document.getElementById('chartDom').getContext('2d');
    new Chart(ctx, {{
        type: 'doughnut',
        data: {{
            labels: ['BTC', 'ETH', 'SOL', 'Otros'],
            datasets: [{{
                data: [52.4, 17.2, 3.5, 26.9],
                backgroundColor: ['#F7931A', '#627EEA', '#14F195', '#2e2e2e'],
                borderWidth: 2,
                borderColor: '#0e1117',
                hoverOffset: 15
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: true,
            plugins: {{
                legend: {{ 
                    position: 'bottom', 
                    labels: {{ color: '#9ca3af', font: {{ size: 12 }}, padding: 20, usePointStyle: true }} 
                }}
            }},
            cutout: '75%'
        }}
    }});
</script>
"""

components.html(layout_final, height=450)