import streamlit as st
import pandas as pd
import urllib.parse
from PIL import Image

# Configuración limpia estilo E-commerce móvil
st.set_page_config(
    page_title="A&G Ventas",
    page_icon="🛍️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilos minimalistas tipo Mercado Libre (Blanco, gris suave y azul corporativo)
st.markdown("""
    <style>
    .stApp {
        background-color: #ededed;
        color: #333333;
    }
    .card {
        background-color: #ffffff;
        padding: 12px;
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.08);
        margin-bottom: 12px;
    }
    .price {
        font-size: 22px;
        font-weight: 700;
        color: #2d3238;
    }
    .installments {
        color: #00a650;
        font-weight: 600;
        font-size: 13px;
    }
    .stButton>button {
        background-color: #3483fa;
        color: white;
        border-radius: 6px;
        font-weight: bold;
        border: none;
        height: 40px;
    }
    .stButton>button:hover {
        background-color: #2968c8;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Título minimalista
st.markdown("<h3 style='text-align: center; margin-bottom: 0; color: #333;'>🛍️ A&G VENTAS</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 13px;'>Canal Exclusivo Comercial</p>", unsafe_allow_html=True)

# Memoria de productos
if "productos" not in st.session_state:
    st.session_state["productos"] = [
        {
            "nombre": "Mesa Industrial 1.60m",
            "precio": 350000.0,
            "img": "https://images.unsplash.com/photo-1615066390971-03e4e1c36ddf?auto=format&fit=crop&w=600&q=80",
            "desc": "Hierro y madera listonada."
        },
        {
            "nombre": "Juego Sillas Tapizadas x4",
            "precio": 220000.0,
            "img": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?auto=format&fit=crop&w=600&q=80",
            "desc": "Estructura reforzada."
        }
    ]

# Pestañas limpias
tab_shop, tab_calc, tab_add = st.tabs(["🛒 Catálogo", "🧮 Simular Cuotas", "➕ Nuevo Mueble"])

# ==========================================
# 1. CATÁLOGO RÁPIDO
# ==========================================
with tab_shop:
    buscar = st.text_input("🔍 Buscar mueble...", placeholder="Ej: Mesa, Silla...")
    
    filtrados = [p for p in st.session_state["productos"] if buscar.lower() in p["nombre"].lower()]

    for i, prod in enumerate(filtrados):
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            # Mostrar imagen (sea URL o archivo subido)
            st.image(prod["img"], use_container_width=True)
            
            st.markdown(f"**{prod['nombre']}**")
            st.markdown(f"<span style='color: #666; font-size: 12px;'>{prod['desc']}</span>", unsafe_allow_html=True)
            st.markdown(f'<div class="price">$ {prod["precio"]:,.2f}</div>', unsafe_allow_html=True)
            st.markdown('<div class="installments">⚡ 3 y 6 cuotas disponibles</div>', unsafe_allow_html=True)
            
            # Envío rápido por WhatsApp
            tel = st.text_input("Celular del cliente (ej: 3764xxxxxx)", key=f"t_{i}")
            if st.button("💬 Enviar Presupuesto por WhatsApp", key=f"b_{i}", use_container_width=True):
                if not tel.strip():
                    st.warning("⚠️ Ingresa el número.")
                else:
                    msg = f"¡Hola! 👋 Te enviamos la cotización de *Mueblería A&G*:\n\n🪑 *{prod['nombre']}*\n💰 *Precio Contado:* ${prod['precio']:,.2f}\n\n¿Coordinamos la seña?"
                    link = f"https://api.whatsapp.com/send?phone=549{tel.strip()}&text={urllib.parse.quote(msg)}"
                    st.markdown(f'<meta http-equiv="refresh" content="0;url={link}">', unsafe_allow_html=True)
                    st.success("✅ ¡Abriendo WhatsApp!")
            
            st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 2. SIMULADOR DE CUOTAS EXPRESS
# ==========================================
with tab_calc:
    st.subheader("🧮 Calcular Cuotas")
    
    nombres = [p["nombre"] for p in st.session_state["productos"]] + ["Monto Libre"]
    elegido = st.selectbox("Producto", options=nombres)
    
    if elegido == "Monto Libre":
        base = st.number_input("Monto total ($)", min_value=1000.0, value=200000.0, step=5000.0)
    else:
        obj = next(p for p in st.session_state["productos"] if p["nombre"] == elegido)
        base = obj["precio"]
        st.caption(f"Precio base: $ {base:,.2f}")

    cuotas = st.selectbox("Plazo", options=[1, 3, 6, 9, 12], index=2)
    interes_mensual = st.slider("Interés Mensual (%)", 0.0, 15.0, 4.0, 0.5)

    # Cálculo financiero simple
    total_fin = base * ((1 + (interes_mensual / 100)) ** cuotas)
    valor_c = total_fin / cuotas

    st.markdown("---")
    st.metric(label=f"💳 {cuotas} Cuotas de", value=f"$ {valor_c:,.2f}")
    st.markdown(f"**Total Financiado:** <span style='color: #00a650;'>$ {total_fin:,.2f}</span>", unsafe_allow_html=True)

    tel_c = st.text_input("Celular del cliente para la simulación")
    if st.button("📤 Enviar Simulación por WhatsApp", use_container_width=True):
        if not tel_c.strip():
            st.warning("⚠️ Ingresa el número.")
        else:
            msg_c = f"📊 *PLAN DE FINANCIACIÓN - A&G*\n\n🛍️ {elegido}\n💳 {cuotas} cuotas de ${valor_c:,.2f}\n💰 Total: ${total_fin:,.2f}"
            link_c = f"https://api.whatsapp.com/send?phone=549{tel_c.strip()}&text={urllib.parse.quote(msg_c)}"
            st.markdown(f'<meta http-equiv="refresh" content="0;url={link_c}">', unsafe_allow_html=True)
            st.success("✅ ¡Abriendo WhatsApp!")

# ==========================================
# 3. SUBIR NUEVO MUEBLE (CON FOTO DESDE CELU/PC)
# ==========================================
with tab_add:
    st.subheader("➕ Agregar Mueble")
    
    with st.form("form_add"):
        nom = st.text_input("Nombre del Mueble")
        precio = st.number_input("Precio Contado ($)", min_value=1.0, value=100000.0, step=5000.0)
        desc = st.text_input("Breve descripción")
        
        # Widget para subir imagen desde el celular o computadora
        foto_subida = st.file_uploader("Subir Foto del Mueble", type=["jpg", "png", "jpeg"])
        
        guardar = st.form_submit_button("💾 Guardar en Catálogo")
        
        if guardar:
            if not nom.strip():
                st.error("⚠️ Ponle un nombre al mueble.")
            else:
                # Si subió una foto la guardamos, sino usa una por defecto
                if foto_subida is not None:
                    img_path = foto_subida
                else:
                    img_path = "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=600&q=80"
                
                st.session_state["productos"].append({
                    "nombre": nom.strip(),
                    "precio": precio,
                    "img": img_path,
                    "desc": desc.strip()
                })
                st.success(f"🎉 ¡{nom} agregado con éxito al catálogo de ventas!")
