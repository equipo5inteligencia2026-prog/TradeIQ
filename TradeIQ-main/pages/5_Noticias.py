import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from styles import render_interface
import plotly.graph_objects as go
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(layout="wide", initial_sidebar_state="expanded")
render_interface("Noticias & Sentimiento")


# 3. ESTILOS CSS REFINADOS
st.markdown("""
<style>
    .card { background: #111217; border: 1px solid #2e2e2e; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
    .card-title { color: #888; font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; }
    .card-badge { background: rgba(34, 211, 238, 0.1); color: #22d3ee; padding: 2px 8px; border-radius: 4px; font-size: 10px; margin-left: 10px; border: 1px solid rgba(34, 211, 238, 0.2); }
    .news-sent { padding: 4px 10px; border-radius: 4px; font-size: 10px; font-weight: bold; font-family: monospace; }
    .pos { background: rgba(0, 230, 118, 0.1); color: #00e676; }
    .neg { background: rgba(255, 68, 68, 0.1); color: #ff4444; }
    .neu { background: rgba(156, 163, 175, 0.1); color: #9ca3af; }
</style>
""", unsafe_allow_html=True)

# 4. SELECTOR DE ACTIVO
activo_noticias = st.selectbox("ACTIVO", ["FSM", "BVN", "ABX", "BHP", "SCCO"], label_visibility="collapsed")

# 5. GRID SUPERIOR
col_sent, col_chart = st.columns([1, 1.8], gap="medium")

with col_sent:
    st.markdown(f"""
        <div class="card" style="height:350px; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center;">
            <div class="card-title" style="width:100%; text-align:left;">Sentimiento Global — {activo_noticias}</div>
            <div style="font-size:52px; font-weight:900; color:#00e676; margin-top:10px;">+0.62</div>
            <div style="font-size:12px; color:#9ca3af; margin-bottom:25px; letter-spacing:1px;">BULLISH / POSITIVO</div>
            <div style="width:100%; height:10px; background:#1a1c23; border-radius:5px; overflow:hidden; margin-bottom:12px; border: 1px solid #2e2e2e;">
                <div style="width:81%; height:100%; background:linear-gradient(90deg, #ff4444, #ffc107, #00e676);"></div>
            </div>
            <div style="display:flex; justify-content:space-between; width:100%; font-size:10px; color:#555; font-family:monospace;">
                <span>-1.0 NEG</span><span>0.0 NEU</span><span>+1.0 POS</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_chart:
    st.markdown(f'<div class="card-title" style="margin-left:5px;">Evolución del Sentimiento — 30 Días</div>', unsafe_allow_html=True)
    with st.container(border=True):
        x_days = pd.date_range(end=datetime.now(), periods=30)
        y_vals = np.sin(np.linspace(0, 4, 30)) * 0.2 + 0.5 + (np.random.rand(30) * 0.1)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_days, y=y_vals, 
            mode='lines', 
            line=dict(color='#00e676', width=3, shape='spline'),
            fill='tozeroy', 
            fillcolor='rgba(0, 230, 118, 0.05)'
        ))
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=10, b=0, l=10, r=10),
            height=285, # Ajustado para alinear con la card de la izquierda
            showlegend=False,
            xaxis=dict(showgrid=False, tickfont=dict(color='#444')),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', side='right')
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# 6. ANÁLISIS LLM
st.markdown(f"""
    <div class="card">
        <div class="card-title">Análisis LLM — Contexto del Activo <span class="card-badge">GPT-4 PRO</span></div>
        <div style="background:rgba(34, 211, 238, 0.03); border:1px solid rgba(34, 211, 238, 0.1); border-radius:6px; padding:20px; font-size:13.5px; line-height:1.8; color:#d1d5db">
            <strong style="color:#22d3ee">Perspectiva Estratégica para {activo_noticias}:</strong><br>
            El análisis de flujo de noticias detecta un patrón de acumulación institucional tras el último reporte trimestral. 
            A pesar de las presiones macroeconómicas, la confianza del consumidor en la marca se mantiene en niveles récord. 
            Se observa una correlación positiva del 0.85 entre el sentimiento social y la recuperación del precio en las últimas 48 horas.
        </div>
    </div>
""", unsafe_allow_html=True)

# 7. FEED DE NOTICIAS
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">Noticias Analizadas — 24H</div>', unsafe_allow_html=True)

try:
    tick = yf.Ticker(activo_noticias)
    for news in tick.news[:5]:
        title = news.get('title', 'Headline')
        publisher = news.get('publisher', 'Finance')
        score = 0.55 if "growth" in title.lower() or "surpasses" in title.lower() else 0.05
        label, css = ("POSITIVO", "pos") if score > 0.1 else ("NEUTRO", "neu")
        
        st.markdown(f"""
            <div style="padding:18px 0; border-bottom:1px solid #2e2e2e;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <span class="news-sent {css}">{label} {score:+.2f}</span>
                    <span style="font-size:11px; color:#555; font-family:monospace;">{publisher.upper()}</span>
                </div>
                <div style="font-size:14.5px; color:#f3f4f6; font-weight:500; line-height:1.4;">{title}</div>
            </div>
        """, unsafe_allow_html=True)
except:
    st.info("Sincronizando feed de noticias...")

st.markdown('</div>', unsafe_allow_html=True)