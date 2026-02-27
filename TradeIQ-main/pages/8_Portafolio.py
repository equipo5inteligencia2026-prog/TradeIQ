import streamlit as st
import plotly.graph_objects as go
from styles import render_interface

# 1. CONFIGURACIÓN E INYECCIÓN DE ESTILOS
st.set_page_config(layout="wide")
render_interface("Portafolio & Posiciones")

st.markdown("""
<style>
    .card { background: #111217; border: 1px solid #2e2e2e; border-radius: 8px; padding: 24px; margin-bottom: 20px; }
    .card-title { color: #888; font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 20px; }
    
    /* Row de KPIs */
    .kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 30px; }
    .kpi { background: #111217; border: 1px solid #2e2e2e; padding: 20px; border-radius: 8px; }
    .kpi-label { font-size: 10px; color: #666; font-family: monospace; margin-bottom: 8px; }
    .kpi-val { font-size: 24px; font-weight: bold; color: white; }
    .kpi-change { font-size: 11px; margin-top: 8px; font-weight: 500; }
    
    /* Info de Portafolio Lateral */
    .port-item { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; font-size: 13px; }
    .port-dot { width: 8px; height: 8px; border-radius: 50%; }
    .port-sym { font-weight: bold; color: black; width: 45px; }
    .port-pct { color: #666; width: 40px; }
    .port-pnl { font-family: monospace; font-weight: bold; margin-left: auto; }
    
    .up { color: #00e676; }
    .dn { color: #ff4444; }
    .nu { color: #9ca3af; }

    /* Tabla Estilizada */
    .tbl-container { width: 100%; overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    th { text-align: left; color: #555; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 12px 8px; border-bottom: 1px solid #2e2e2e; }
    td { padding: 16px 8px; border-bottom: 1px solid #1a1c23; font-size: 13px; color: #eee; }
    .btn-sell { background: transparent; border: 1px solid #333; color: #888; padding: 6px 14px; font-size: 10px; border-radius: 4px; cursor: pointer; transition: 0.3s; }
    .btn-sell:hover { border-color: #ff4444; color: #ff4444; background: rgba(255,68,68,0.05); }
</style>
""", unsafe_allow_html=True)

# 2. KPI ROW SUPERIOR
st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi">
            <div class="kpi-label">VALOR TOTAL</div>
            <div class="kpi-val">$48,320</div>
            <div class="kpi-change up">▲ +$1,240 hoy</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">RETORNO TOTAL</div>
            <div class="kpi-val up">+24.8%</div>
            <div class="kpi-change up">Desde inicio</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">EFECTIVO DISPONIBLE</div>
            <div class="kpi-val">$4,280</div>
            <div class="kpi-change nu">8.8% del portafolio</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">POSICIONES ABIERTAS</div>
            <div class="kpi-val">6</div>
            <div class="kpi-change up">▲ 5 en ganancia</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# 3. GRID CENTRAL
col_dist, col_perf = st.columns([1, 1], gap="large")

with col_dist:
    st.markdown('<div class="card-title">Distribución del Portafolio</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        labels = ["FSM", "BVN", "ABX", "BHP", "SCCO"]
        values = [32, 24, 18, 14, 12]
        colors = ['#00d4ff', '#00e676', '#ffb300', '#ff4444', '#7c4dff']
        fig_donut = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.75, marker=dict(colors=colors))])
        fig_donut.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=220, paper_bgcolor='rgba(0,0,0,0)')
        fig_donut.update_traces(textinfo='none', hoverinfo='label+percent')
        st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False})
    with c2:
        st.markdown(f"""
            <div style="padding-top: 10px;">
                <div class="port-item"><div class="port-dot" style="background:#00d4ff"></div><span class="port-sym">AAPL</span><span class="port-pct">32%</span><span class="port-pnl up">+$3,840</span></div>
                <div class="port-item"><div class="port-dot" style="background:#00e676"></div><span class="port-sym">NVDA</span><span class="port-pct">24%</span><span class="port-pnl up">+$2,880</span></div>
                <div class="port-item"><div class="port-dot" style="background:#ffb300"></div><span class="port-sym">TSLA</span><span class="port-pct">18%</span><span class="port-pnl dn">-$432</span></div>
                <div class="port-item"><div class="port-dot" style="background:#ff4444"></div><span class="port-sym">BTC</span><span class="port-pct">14%</span><span class="port-pnl up">+$2,016</span></div>
                <div class="port-item"><div class="port-dot" style="background:#7c4dff"></div><span class="port-sym">MSFT</span><span class="port-pct">12%</span><span class="port-pnl up">+$691</span></div>
            </div>
        """, unsafe_allow_html=True)

with col_perf:
    st.markdown('<div class="card-title">Rendimiento Histórico</div>', unsafe_allow_html=True)
    y_data = [40000, 41200, 40500, 43000, 45600, 44800, 48320]
    fig_perf = go.Figure()
    fig_perf.add_trace(go.Scatter(y=y_data, mode='lines', line=dict(color='#00d4ff', width=2, shape='spline'), fill='tozeroy', fillcolor='rgba(0, 212, 255, 0.03)'))
    fig_perf.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=0, l=0, r=0), height=220, showlegend=False, xaxis=dict(showgrid=False, showticklabels=False), yaxis=dict(showgrid=True, gridcolor='#1a1c23', side='right'))
    st.plotly_chart(fig_perf, use_container_width=True, config={'displayModeBar': False})

# 4. TABLA DENTRO DE CARD
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">Posiciones Abiertas</div>', unsafe_allow_html=True)
st.markdown("""
    <div class="tbl-container">
        <table>
            <thead>
                <tr><th>ACTIVO</th><th>CANTIDAD</th><th>P. PROMEDIO</th><th>P. ACTUAL</th><th>P&L $</th><th>P&L %</th><th>ACCIÓN</th></tr>
            </thead>
            <tbody>
                <tr><td style='color:#000'>AAPL</td><td style='color:#000'>80</td><td style='color:#000'>$139.38</td><td style='color:#000'>$187.42</td><td class="up">+$3,840</td><td class="up">+34.5%</td><td><button class="btn-sell">VENDER</button></td></tr>
                <tr><td style='color:#000'>NVDA</td><td style='color:#000'>14</td><td style='color:#000'>$668.00</td><td style='color:#000'>$875.20</td><td class="up">+$2,900</td><td class="up">+31.0%</td><td><button class="btn-sell">VENDER</button></td></tr>
                <tr><td style='color:#000'>TSLA</td><td style='color:#000'>36</td><td style='color:#000'>$254.10</td><td style='color:#000'>$242.10</td><td class="dn">-$432</td><td class="dn">-4.7%</td><td><button class="btn-sell">VENDER</button></td></tr>
                <tr><td style='color:#000'>MSFT</td><td style='color:#000'>13</td><td style='color:#000'>$362.70</td><td style='color:#000'>$415.80</td><td class="up">+$691</td><td class="up">+14.6%</td><td><button class="btn-sell">VENDER</button></td></tr>
            </tbody>
        </table>
    </div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)