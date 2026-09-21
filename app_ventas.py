import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime

# Configuración de página estilo E-commerce
st.set_page_config(
    page_title="A&G Ventas - Catálogo Oficial",
    page_icon="🛍️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilos CSS tipo Mercado Libre / Mercado Pago (Fondo limpio, azul corporativo y naranja A&G)
st.markdown("""
    <style>
    .stApp {
        background-color: #f5f6f8;
        color: #333333;
    }
    .product-card {
        background-color: #ffffff;
        padding: 16px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 16px;
        border: 1px solid #e0e0e0;
    }
    .price-tag {
        font-size: 24px;
        font-weight: bold;
        color: #333333;
    }
    .installments {
        color: #00a650;
        font-weight: bold;
        font-size: 14px;
    }
    .stButton>button {
        background-color: #3483fa;
        color: white;
        border-radius: 6px;
        font-weight: bold;
        border: none;
        height: 42px;
    }
    .stButton>button:hover {
        background-color: #2968c8;
        color: white;
    }
    .whatsapp-btn>button {
        background-color: #25d366 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("<h2 style='text-align: center; color: #333333;'>🛍️ A&G VENTAS PRO</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Canal Exclusivo para Equipo de Ventas</p>", unsafe_allow_html=True)
st.markdown("---")

# --- BASE DE DATOS DE PRODUCTOS (Se puede conectar a Google Sheets) ---
# Simulamos un inventario inicial o leemos de una pestaña "catalogo" de tu Google Sheet
if "productos" not in st.session_state:
    st.session_state["productos"] = [
        {"nombre": "Mesa Estilo Industrial 1.60m", "precio": 350000.0, "categoria": "Muebles", "img": "https://images.unsplash.com/photo-1615066390971-03e4e1c36ddf?auto=format&fit=crop&w=600&q=80", "desc": "Estructura de hierro robusta y madera listonada."},
        {"nombre": "Juego de Sillas X x4 unidades", "precio": 220000.0, "categoria": "Muebles", "img": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?auto=format&fit=crop&w=600&q=80", "desc": "Ergonómicas, tapizado talampaya reforzado."},
        {"nombre": "Ropero 3 Puertas Corredizas", "precio": 580000.0, "categoria": "Muebles", "img": "https://images.unsplash.com/photo-1595428774223-ef52624120d2?auto=format&fit=crop&w=600&q=80", "desc": "Melamina de primera calidad con perfilería de aluminio."},
        {"nombre": "Portón Corredizo Metálico a Medida", "precio": 750000.0, "categoria": "A.J Gestión Urbana", "img": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=600&q=80", "desc": "Trabajo pesado en herrería con diseño moderno."}
    ]

# --- NAVEGACIÓN RÁPIDA (PESTAÑAS) ---
tab_catalogo, tab_calculadora, tab_cargar = st.tabs(["🛒 Catálogo", "🧮 Simulador de Cuotas", "➕ Nuevo Producto"])

# ==========================================
# 1. CATÁLOGO TIPO MERCADO LIBRE
# ==========================================
with tab_catalogo:
    busqueda = st.text_input("🔍 Buscar producto...", placeholder="Ej: Mesa, Silla, Portón...")
    
    # Filtro de búsqueda
    productos_filtrados = [
        p for p in st.session_state["productos"] 
        if busqueda.lower() in p["nombre"].lower() or busqueda.lower() in p["categoria"].lower()
    ]

    for idx, prod in enumerate(productos_filtrados):
        with st.container():
            st.markdown(f"""
                <div class="product-card">
                    <img src="{prod['img']}" style="width: 100%; height: 200px; object-fit: cover; border-radius: 6px;">
                    <h4 style="margin: 10px 0 5px 0; color: #111;">{prod['nombre']}</h4>
                    <p style="color: #666; font-size: 13px; margin-bottom: 8px;">{prod['desc']}</p>
                    <div class="price-tag">$ {prod['precio']:,.2f}</div>
                    <div class="installments">⚡ En hasta 12 cuotas sin interés con tarjetas seleccionadas</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Botón rápido para enviar presupuesto de este producto por WhatsApp
            tel_cliente = st.text_input(f"Celular del cliente (Ej: 3764XXXXXX)", key=f"tel_{idx}")
            if st.button(f"💬 Enviar Presupuesto por WhatsApp", key=f"btn_wsp_{idx}", use_container_width=True):
                if not tel_cliente.strip():
                    st.warning("⚠️ Ingresa el número del cliente.")
                else:
                    texto_wsp = f"¡Hola! 👋 Te enviamos la cotización desde *Mueblería A&G*:\n\n" \
                                f"🪑 *{prod['nombre']}*\n" \
                                f"📝 {prod['desc']}\n" \
                                f"💰 *Precio Contado / Efectivo:* ${prod['precio']:,.2f}\n\n" \
                                f"¿Te gustaría coordinar la seña o ver opciones de financiación?"
                    
                    url_wsp = f"https://api.whatsapp.com/send?phone=549{tel_cliente.strip()}&text={urllib.parse.quote(texto_wsp)}"
                    st.markdown(f'<meta http-equiv="refresh" content="0;url={url_wsp}">', unsafe_allow_html=True)
                    st.success("✅ ¡Abriendo WhatsApp con el presupuesto listo!")
            st.markdown("---")

# ==========================================
# 2. SIMULADOR DE CUOTAS (ESTILO MP)
# ==========================================
with tab_calculadora:
    st.subheader("🧮 Simulador de Financiación")
    
    # Seleccionar producto o ingresar monto libre
    nombres_prods = [p["nombre"] for p in st.session_state["productos"]] + ["Otro (Monto Libre)"]
    prod_elegido = st.selectbox("Seleccionar Producto", options=nombres_prods)
    
    if prod_elegido == "Otro (Monto Libre)":
        monto_base = st.number_input("Monto Total del Mueble / Servicio ($)", min_value=1000.0, value=300000.0, step=10000.0)
    else:
        p_obj = next(p for p in st.session_state["productos"] if p["nombre"] == prod_elegido)
        monto_base = p_obj["precio"]
        st.info(f"Precio base seleccionado: **$ {monto_base:,.2f}**")

    col_cuotas, col_interes = st.columns(2)
    with col_cuotas:
        cant_cuotas = st.selectbox("Cantidad de Cuotas", options=[1, 3, 6, 9, 12, 18, 24], index=2)
    with col_interes:
        tasa_mensual = st.number_input("Interés Mensual Estimado (%)", min_value=0.0, value=4.0, step=0.5)

    # Cálculo financiero (Interés compuesto / sistema francés básico)
    if tasa_mensual > 0:
        i = tasa_mensual / 100
        monto_total = monto_base * ((1 + i) ** cant_cuotas)
    else:
        monto_total = monto_base
        
    valor_cuota = monto_total / cant_cuotas

    st.markdown("---")
    st.metric(label=f"💳 Valor de cada cuota ({cant_cuotas} cuotas)", value=f"$ {valor_cuota:,.2f}")
    st.markdown(f"**Total Financiado:** <span style='color: #00a650; font-size: 20px;'>$ {monto_total:,.2f}</span>", unsafe_allow_html=True)

    tel_sim = st.text_input("Celular del Cliente para enviar simulación (Ej: 3764XXXXXX)")
    if st.button("📤 Enviar Simulación por WhatsApp", use_container_width=True):
        if not tel_sim.strip():
            st.warning("⚠️ Ingresa el número del cliente.")
        else:
            texto_sim = f"📊 *SIMULACIÓN DE FINANCIACIÓN - MUEBLERÍA A&G*\n\n" \
                        f"🛍️ *Concepto:* {prod_elegido}\n" \
                        f"💰 *Total Financiado:* ${monto_total:,.2f}\n" \
                        f"💳 *Plan:* {cant_cuotas} cuotas de ${valor_cuota:,.2f}\n\n" \
                        f"¡Aprovecha esta financiación para renovar tus espacios!"
            
            url_sim = f"https://api.whatsapp.com/send?phone=549{tel_sim.strip()}&text={urllib.parse.quote(texto_sim)}"
            st.markdown(f'<meta http-equiv="refresh" content="0;url={url_sim}">', unsafe_allow_html=True)
            st.success("✅ ¡Abriendo WhatsApp con el plan de cuotas!")

# ==========================================
# 3. CARGAR NUEVO PRODUCTO AL CATÁLOGO
# ==========================================
with tab_cargar:
    st.subheader("➕ Agregar Producto al Catálogo")
    
    with st.form("form_nuevo_prod"):
        nom_nuevo = st.text_input("Nombre del Mueble o Producto")
        cat_nuevo = st.selectbox("Categoría", options=["Muebles", "Línea Blanca", "A.J Gestión Urbana", "Metalúrgica"])
        precio_nuevo = st.number_input("Precio Contado ($)", min_value=1.0, value=150000.0, step=5000.0)
        desc_nuevo = st.text_area("Descripción breve")
        img_nuevo = st.text_input("URL de la Imagen (Opcional, deja en blanco para usar genérica)")
        
        submitted = st.form_submit_button("💾 Guardar en el Catálogo")
        if submitted:
            if not nom_nuevo.strip():
                st.error("⚠️ El nombre es obligatorio.")
            else:
                imagen_final = img_nuevo.strip() if img_nuevo.strip() else "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=600&q=80"
                st.session_state["productos"].append({
                    "nombre": nom_nuevo.strip(),
                    "precio": precio_nuevo,
                    "categoria": cat_nuevo,
                    "img": imagen_final,
                    "desc": desc_nuevo.strip()
                })
                st.success(f"🎉 ¡Producto **{nom_nuevo}** agregado con éxito al catálogo de ventas!")