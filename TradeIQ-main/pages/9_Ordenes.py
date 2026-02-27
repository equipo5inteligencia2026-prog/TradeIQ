import streamlit as st
import pandas as pd
from datetime import datetime
from styles import render_interface

# 1. CONFIGURACIÓN E INYECCIÓN DE ESTILOS
st.set_page_config(layout="wide")
render_interface("Órdenes & Ejecuciones")
st.markdown("""
<style>
    /* Títulos de sección planos */
    .section-header { 
        color: #888; font-size: 11px; font-weight: bold; 
        text-transform: uppercase; letter-spacing: 1px; 
        margin-bottom: 20px; border-bottom: 1px solid #2e2e2e; padding-bottom: 8px;
    }
    
    .card-badge { background: rgba(0, 230, 118, 0.1); color: #00e676; padding: 4px 10px; border-radius: 4px; font-size: 10px; font-weight: 800; border: 1px solid rgba(0, 230, 118, 0.2); float: right; }
    
    /* Resumen de Orden */
    .order-confirm { background: #1a1c23; border: 1px solid #2e2e2e; border-radius: 6px; padding: 20px; margin-top: 10px; margin-bottom: 20px; }
    .summary-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 13px; }
    .summary-label { color: #666; }
    .summary-val { color: white; font-weight: 700; text-align: right; }
    
    /* Tabla Estilo Terminal */
    .tbl-container { width: 100%; }
    .order-table { width: 100%; border-collapse: collapse; color: #eee; }
    .order-table th { text-align: left; color: #555; font-size: 10px; padding: 12px 8px; border-bottom: 1px solid #2e2e2e; text-transform: uppercase; }
    .order-table td { padding: 16px 8px; border-bottom: 1px solid #1a1c23; font-size: 12px; }
    
    .up { color: #00e676; font-weight: bold; }
    .dn { color: #ff4444; font-weight: bold; }
    .status-pill { background: rgba(0, 230, 118, 0.1); color: #00e676; padding: 3px 8px; border-radius: 4px; font-size: 9px; font-weight: bold; border: 1px solid rgba(0, 230, 118, 0.2); }
</style>
""", unsafe_allow_html=True)

# 2. INICIALIZACIÓN DEL ESTADO
if 'order_history' not in st.session_state:
    st.session_state.order_history = [
        {"hora": "10:32", "activo": "AAPL", "tipo": "COMPRA", "cant": 5, "precio": 184.10, "estado": "EJECUTADA"},
        {"hora": "09:15", "activo": "NVDA", "tipo": "COMPRA", "cant": 2, "precio": 872.50, "estado": "EJECUTADA"},
        {"hora": "08:55", "activo": "TSLA", "tipo": "VENTA", "cant": 10, "precio": 245.30, "estado": "EJECUTADA"},
    ]

# 3. GRID PRINCIPAL
col_form, col_hist = st.columns([1.1, 1.9], gap="large")

with col_form:
    st.markdown('<div class="section-header">Nueva Orden <span class="card-badge">● IB CONECTADO</span></div>', unsafe_allow_html=True)
    
    o_type = st.selectbox("OPERACIÓN", ["COMPRA", "VENTA", "SHORT"])
    o_asset = st.selectbox("ACTIVO", ["AAPL", "TSLA", "NVDA", "MSFT", "BTC"])
    o_qty = st.number_input("CANTIDAD", min_value=1, value=10)
    
    precio_mercado = {"AAPL": 187.42, "TSLA": 242.10, "NVDA": 875.20, "MSFT": 415.80, "BTC": 62100.00}
    o_price = precio_mercado.get(o_asset, 100.0)
    
    valor_total = o_qty * o_price
    color_clase = "up" if o_type == "COMPRA" else "dn"

    # Resumen Compacto
    st.markdown(f'<div class="order-confirm"><div class="summary-grid"><span class="summary-label">Tipo:</span><span class="summary-val {color_clase}">{o_type}</span><span class="summary-label">Símbolo:</span><span class="summary-val">{o_asset}</span><span class="summary-label">Total Est.:</span><span class="summary-val">${valor_total:,.2f}</span></div></div>', unsafe_allow_html=True)

    if st.button("CONFIRMAR Y ENVIAR ORDEN →", type="primary", use_container_width=True):
        nueva_orden = {
            "hora": datetime.now().strftime("%H:%M"),
            "activo": o_asset,
            "tipo": o_type,
            "cant": o_qty,
            "precio": o_price,
            "estado": "EJECUTADA"
        }
        st.session_state.order_history.insert(0, nueva_orden)
        st.rerun()

with col_hist:
    st.markdown('<div class="section-header">Historial de Ejecuciones</div>', unsafe_allow_html=True)
    
    # Construcción de filas compactas
    filas_html = ""
    for order in st.session_state.order_history:
        clase_tipo = "up" if order['tipo'] == "COMPRA" else "dn"
        filas_html += f"<tr><td style='color:#000'>{order['hora']}</td><td style='color:#000'><b>{order['activo']}</b></td><td class='{clase_tipo}'>{order['tipo']}</td><td style='color:#000'>{order['cant']}</td><td style='color:#000'>${order['precio']:,.2f}</td><td><span class='status-pill'>{order['estado']}</span></td></tr>"
    # Renderizado de tabla directo
    tabla_final = f'<div class="tbl-container"><table class="order-table"><thead><tr><th>Hora</th><th>Activo</th><th>Tipo</th><th>Cant.</th><th>Precio</th><th>Estado</th></tr></thead><tbody>{filas_html}</tbody></table></div>'
    
    st.markdown(tabla_final, unsafe_allow_html=True)