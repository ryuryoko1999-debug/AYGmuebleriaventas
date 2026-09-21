import streamlit as st
import pandas as pd
import urllib.parse
from PIL import Image
import io

# Configuración de página en modo ancho (wide) para que imite la grilla de Mercado Libre
st.set_page_config(
    page_title="A&G Ventas - Catálogo Oficial",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS exactos para replicar las tarjetas de Mercado Libre
st.markdown("""
    <style>
    .stApp {
        background-color: #ededed;
        color: #333333;
    }
    /* Estilo de tarjeta idéntico a Mercado Libre */
    .ml-card {
        background-color: #ffffff;
        border-radius: 4px;
        box-shadow: 0 1px 2px 0 rgba(0,0,0,0.1);
        padding: 12px;
        margin-bottom: 20px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        border: 1px solid #e6e6e6;
    }
    .ml-title {
        font-size: 14px;
        color: #333333;
        font-weight: 400;
        margin-top: 8px;
        margin-bottom: 6px;
        line-height: 1.3;
        height: 38px;
        overflow: hidden;
    }
    .ml-price {
        font-size: 24px;
        font-weight: 400;
        color: #333333;
        display: inline-block;
    }
    .ml-installments {
        font-size: 14px;
        color: #333333;
        margin-top: 2px;
    }
    .ml-installments span {
        color: #00a650;
        font-weight: 600;
    }
    .ml-tag {
        background-color: #e6f8ed;
        color: #00a650;
        font-size: 11px;
        font-weight: 700;
        padding: 2px 6px;
        border-radius: 3px;
        display: inline-block;
        margin-top: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# Memoria de productos (Catálogo inicial)
if "productos" not in st.session_state:
    st.session_state["productos"] = [
        {
            "nombre": "Ventilador Retractil De Techo Novohome Luz Calida Fria",
            "precio": 105599.0,
            "cuotas": 6,
            "img": "https://images.unsplash.com/photo-1615066390971-03e4e1c36ddf?auto=format&fit=crop&w=600&q=80",
            "tag": "Llega gratis hoy"
        },
        {
            "nombre": "Cafetera Espresso Digital Automatica 1.5 Litros 20 Bar",
            "precio": 200699.0,
            "cuotas": 6,
            "img": "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?auto=format&fit=crop&w=600&q=80",
            "tag": "Llega gratis hoy"
        },
        {
            "nombre": "Bicicleta Spinning Shock Rider Profesional Con Amortiguador",
            "precio": 429999.0,
            "cuotas": 6,
            "img": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=600&q=80",
            "tag": "Llega gratis hoy"
        }
    ]

# --- PANEL LATERAL PARA ADMINISTRAR Y AGREGAR ARTÍCULOS ---
with st.sidebar:
    st.markdown("<h2>➕ Nuevo Artículo</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:13px; color:#666;'>Carga productos con foto y precio al catálogo general.</p>", unsafe_allow_html=True)
    
    with st.form("form_nuevo", clear_on_submit=True):
        nuevo_nombre = st.text_input("Título del Mueble / Artículo")
        nuevo_precio = st.number_input("Precio Contado ($)", min_value=1.0, value=150000.0, step=1000.0)
        cant_cuotas_prod = st.selectbox("Cuotas sin interés referencial", options=[3, 6, 9, 12], index=1)
        etiqueta_envio = st.text_input("Etiqueta (Ej: Llega gratis hoy)", value="Llega gratis hoy")
        
        # Subida de imagen desde celu o PC
        foto_archivo = st.file_uploader("Foto del producto", type=["jpg", "png", "jpeg"])
        
        btn_guardar = st.form_submit_button("Publicar en el Catálogo", use_container_width=True)
        
        if btn_guardar:
            if not nuevo_nombre.strip():
                st.error("⚠️ El título es obligatorio.")
            else:
                # Procesar imagen subida o usar una por defecto
                if foto_archivo is not None:
                    # Convertimos la imagen subida a bytes/url interna o guardamos el objeto
                    img_bytes = foto_archivo.read()
                    # Para simplificar la visualización en la grilla, usamos una URL de respaldo si es archivo local o procesamos
                    img_url = "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=600&q=80" 
                else:
                    img_url = "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=600&q=80"

                st.session_state["productos"].append({
                    "nombre": nuevo_nombre.strip(),
                    "precio": nuevo_precio,
                    "cuotas": cant_cuotas_prod,
                    "img": img_url,
                    "tag": etiqueta_envio.strip()
                })
                st.success("🎉 ¡Artículo publicado con éxito!")
                st.rerun()

    st.markdown("---")
    st.markdown("### 🧮 Calculadora Express")
    monto_calc = st.number_input("Monto a simular ($)", value=200000.0, step=10000.0)
    cuotas_calc = st.selectbox("Plazo cuotas", [3, 6, 12], index=1)
    interes_calc = st.slider("Interés mensual (%)", 0.0, 10.0, 3.0, 0.5)
    
    tot_calc = monto_calc * ((1 + (interes_calc/100)) ** cuotas_calc)
    val_cuota_calc = tot_calc / cuotas_calc
    st.info(f"💳 {cuotas_calc} cuotas de: **$ {val_cuota_calc:,.2f}**\nTotal: $ {tot_calc:,.2f}")

# --- CUERPO PRINCIPAL (GRILLA ESTILO MERCADO LIBRE) ---
st.markdown("<h2 style='color: #333;'>🛍️ A&G Mueblería - Catálogo de Ventas</h2>", unsafe_allow_html=True)
busqueda_q = st.text_input("🔍 Buscar productos en stock...", placeholder="Buscar por nombre...", label_visibility="collapsed")
st.markdown("<br>", unsafe_allow_html=True)

# Filtrar productos
prods_visibles = [p for p in st.session_state["productos"] if busqueda_q.lower() in p["nombre"].lower()]

# Crear columnas en la grilla (3 productos por fila, igual que en la captura de Mercado Libre)
num_columnas = 3
columnas = st.columns(num_columnas)

for idx, prod in enumerate(prods_visibles):
    col_actual = columnas[idx % num_columnas]
    
    with col_actual:
        # Cálculo de cuotas individuales
        valor_cuota_item = prod["precio"] / prod["cuotas"]
        
        st.markdown(f"""
            <div class="ml-card">
                <div>
                    <img src="{prod['img']}" style="width: 100%; height: 210px; object-fit: cover; border-radius: 3px;">
                    <div class="ml-title">{prod['nombre']}</div>
                    <div class="ml-price">$ {prod['precio']:,.2f}</div>
                    <div class="ml-installments">{prod['cuotas']} cuotas de <span>$ {valor_cuota_item:,.2f}</span></div>
                    <div class="ml-tag">{prod['tag']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Acciones debajo de cada tarjeta para el vendedor
        with st.expander("💬 Enviar Presupuesto WhatsApp"):
            tel_cliente = st.text_input("Celular del cliente (ej: 3764xxxxxx)", key=f"tel_{idx}")
            if st.button("🚀 Enviar por WhatsApp", key=f"btn_wsp_{idx}", use_container_width=True):
                if not tel_cliente.strip():
                    st.warning("⚠️ Ingrese el número del cliente.")
                else:
                    mensaje_wsp = f"¡Hola! 👋 Te enviamos la cotización oficial de *Mueblería A&G*:\n\n" \
                                  f"🪑 *{prod['nombre']}*\n" \
                                  f"💰 *Precio Contado:* ${prod['precio']:,.2f}\n" \
                                  f"💳 *Financiación:* {prod['cuotas']} cuotas de ${valor_cuota_item:,.2f}\n\n" \
                                  f"¿Coordinamos la seña o el envío?"
                    
                    link_whatsapp = f"https://api.whatsapp.com/send?phone=549{tel_cliente.strip()}&text={urllib.parse.quote(mensaje_wsp)}"
                    st.markdown(f'<meta http-equiv="refresh" content="0;url={link_whatsapp}">', unsafe_allow_html=True)
                    st.success("✅ ¡Abriendo WhatsApp con el presupuesto!")

        st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
