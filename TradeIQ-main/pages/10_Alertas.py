import streamlit as st
import pandas as pd
from styles import render_interface

render_interface("Alertas & Notificaciones")
# 1. ESTILOS REFINADOS
st.markdown("""
<style>
    .section-header { 
        color: #888; font-size: 11px; font-weight: bold; 
        text-transform: uppercase; letter-spacing: 1px; 
        margin-bottom: 20px; border-bottom: 1px solid #2e2e2e; padding-bottom: 8px;
    }
    
    /* Contenedor de Alerta Individual */
    .alert-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 0;
        border-bottom: 1px solid #1a1c23;
    }
    
    .alert-info-main { font-size: 14px; color: black; font-weight: 600; }
    .alert-info-sub { font-size: 11px; color: #666; font-family: monospace; margin-top: 4px; }
    
    /* Status Badge */
    .status-on { color: #00e676; font-size: 10px; font-weight: bold; text-transform: uppercase; }
    .status-off { color: #444; font-size: 10px; font-weight: bold; text-transform: uppercase; }
    
    /* Estilo para los selectores de Streamlit para que encajen con el dark mode */
    div[data-baseweb="select"] > div {
        background-color: #1a1c23 ! aspiration;
        border: 1px solid #2e2e2e !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. INICIALIZACIÓN DEL ESTADO
if 'alerts' not in st.session_state:
    st.session_state.alerts = [
        {"activo": "AAPL", "tipo": "Precio superior a", "valor": 195.00, "estado": True, "desc": "Precio superior · Email"},
        {"activo": "BTC", "tipo": "Precio inferior a", "valor": 60000.00, "estado": True, "desc": "Precio inferior · Email"},
        {"activo": "TSLA", "tipo": "Señal IA cambia a ALZA", "valor": 0, "estado": False, "desc": "Señal IA · Email"},
    ]

# 3. GRID PRINCIPAL
col_new, col_list = st.columns([1, 1.5], gap="large")

with col_new:
    st.markdown('<div class="section-header">Nueva Alerta</div>', unsafe_allow_html=True)
    
    with st.container():
        a_asset = st.selectbox("ACTIVO", ["FSM", "BVN", "ABX", "BHP", "SCCO"])
        a_condition = st.selectbox("TIPO DE ALERTA", [
            "Precio superior a", 
            "Precio inferior a", 
            "Variación % diaria", 
            "Señal IA cambia a ALZA", 
            "Señal IA cambia a BAJA"
        ])
        
        # Ocultar umbral si es una señal de IA
        a_value = 0.0
        if "Precio" in a_condition or "Variación" in a_condition:
            a_value = st.number_input("VALOR UMBRAL", value=195.00, step=0.01)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("+ CREAR ALERTA", type="primary", use_container_width=True):
            nueva_alerta = {
                "activo": a_asset,
                "tipo": a_condition,
                "valor": a_value,
                "estado": True,
                "desc": "Señal IA · Email" if "Señal" in a_condition else "Precio/Var · Email"
            }
            st.session_state.alerts.insert(0, nueva_alerta)
            st.rerun()

with col_list:
    st.markdown('<div class="section-header">Alertas Activas</div>', unsafe_allow_html=True)
    
    if not st.session_state.alerts:
        st.info("No hay alertas configuradas.")
    
    for i, alert in enumerate(st.session_state.alerts):
        # Preparar el texto de la alerta
        val_str = f" > ${alert['valor']:,.2f}" if "superior" in alert['tipo'] else f" < ${alert['valor']:,.2f}"
        if "Señal" in alert['tipo']: val_str = " — " + alert['tipo'].split("cambia a ")[1]
        
        # Renderizado de la fila
        with st.container():
            c_info, c_toggle = st.columns([4, 1])
            
            with c_info:
                st.markdown(f"""
                    <div class="alert-item" style="border-bottom: none; padding-bottom: 0;">
                        <div>
                            <div class="alert-info-main">{alert['activo']}{val_str}</div>
                            <div class="alert-info-sub">{alert['desc']}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with c_toggle:
                # Switch de encendido/apagado
                estado_label = "ON" if alert['estado'] else "OFF"
                if st.button(estado_label, key=f"btn_{i}", use_container_width=True):
                    st.session_state.alerts[i]['estado'] = not st.session_state.alerts[i]['estado']
                    st.rerun()
            
            st.markdown('<hr style="margin: 0; border: none; border-bottom: 1px solid #1a1c23;">', unsafe_allow_html=True)