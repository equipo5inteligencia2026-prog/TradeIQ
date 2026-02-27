import streamlit as st
import yfinance as yf
from styles import render_interface
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

# 1. CONFIGURACIÓN
st.set_page_config(layout="wide", initial_sidebar_state="expanded")
st_autorefresh(interval=30000, key="auto_update_acciones")
render_interface("Acciones")

# 2. MAPEO DE TICKERS (IMPORTANTE)
symbol_map = {
    "FSM": "NYSE:FSM",
    "BHP": "NYSE:BHP",
    "BVN": "NYSE:BVN",
    "GOLD": "NYSE:GOLD",   # ABX ahora es GOLD
    "SCCO": "NYSE:SCCO"
}

# 3. DATA FETCHING
@st.cache_data(ttl=60)
def get_stock_info(ticker_symbol):
    try:
        t = yf.Ticker(ticker_symbol)
        return t.info
    except:
        return {}

# 4. BUSCADOR
col_search, _ = st.columns([1, 2])
with col_search:
    symbol = st.selectbox("ACTIVO", list(symbol_map.keys()), label_visibility="collapsed")

tv_symbol = symbol_map[symbol]  # Para TradingView
info = get_stock_info(symbol)   # Para Yahoo Finance

# Manejo seguro de datos
price = info.get('regularMarketPrice') or info.get('currentPrice') or 0
change = info.get('regularMarketChangePercent') or 0
volume = info.get('regularMarketVolume') or 0
avg_volume = info.get('averageVolume') or 0
low_52 = info.get('fiftyTwoWeekLow') or 0
high_52 = info.get('fiftyTwoWeekHigh') or 0
market_cap = info.get('marketCap') or 0
pe_ratio = info.get('trailingPE') or "N/A"
eps = info.get('trailingEps') or 0
roe = (info.get('returnOnEquity') or 0) * 100
debt_equity = info.get('debtToEquity') or 0
dividend_yield = (info.get('dividendYield') or 0) * 100

# 5. DASHBOARD DE KPIs
st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi">
            <div class="kpi-label">PRECIO ACTUAL {symbol}</div>
            <div class="kpi-val">${price:,.2f}</div>
            <div class="kpi-change {'up' if change >= 0 else 'dn'}">{change:+.2f}%</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">VOLUMEN</div>
            <div class="kpi-val">{volume/1e6:.1f}M</div>
            <div class="kpi-change nu">AVG: {avg_volume/1e6:.1f}M</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">RANGO 52W</div>
            <div class="kpi-val" style="font-size:18px">
                ${low_52:,.0f} - ${high_52:,.0f}
            </div>
            <div class="kpi-change nu">LOW / HIGH</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">CAP. MERCADO</div>
            <div class="kpi-val">${market_cap/1e9:,.2f}B</div>
            <div class="kpi-change nu">USD MARKET</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# 6. GRÁFICO DE FRENTE
col_chart, col_side = st.columns([2.5, 1], gap="medium")

with col_chart:
    tv_widget = f"""
    <div style="width: 100%; height: 550px; border-radius: 8px; overflow: hidden; border: 1px solid #2e2e2e;">
        <div id="tradingview_chart" style="height: 100%;"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
          new TradingView.widget({{
          "autosize": true,
          "symbol": "{tv_symbol}",
          "interval": "D",
          "timezone": "Etc/UTC",
          "theme": "dark",
          "style": "1",
          "locale": "es",
          "toolbar_bg": "#1e222d",
          "enable_publishing": false,
          "hide_side_toolbar": false,
          "allow_symbol_change": true,
          "container_id": "tradingview_chart"
        }});
        </script>
    </div>
    """
    components.html(tv_widget, height=560)

with col_side:
    st.markdown(f"""
        <div class="card" style="height: 270px; margin-bottom: 20px; overflow-y: auto;">
            <div class="card-title">PERFIL CORPORATIVO</div>
            <div style="font-size: 13px; color: var(--text); line-height: 1.4;">
                <b style="color:var(--cyan);">{info.get('longName', symbol)}</b><br><br>
                {(info.get('longBusinessSummary') or 'Descripción no disponible.')[:300]}...
            </div>
        </div>
        
        <div class="card" style="height: 320px;">
            <div class="card-title">NÚMEROS CLAVE</div>
            <table class="tbl">
                <tr><td>P/E RATIO</td><td style="text-align:right;">{pe_ratio}</td></tr>
                <tr><td>EPS (TTM)</td><td style="text-align:right;">${eps:.2f}</td></tr>
                <tr><td>ROE</td><td style="text-align:right;">{roe:.2f}%</td></tr>
                <tr><td>DEUDA/CAP</td><td style="text-align:right;">{debt_equity}</td></tr>
                <tr><td>YIELD</td><td style="text-align:right;">{dividend_yield:.2f}%</td></tr>
            </table>
        </div>
    """, unsafe_allow_html=True)