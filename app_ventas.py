import streamlit as st
import pandas as pd
import requests
import json
import base64
import urllib.parse

# Configuración de página en modo ancho (tipo E-commerce)
st.set_page_config(
    page_title="A&G Ventas Pro",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos visuales limpios estilo Mercado Libre / Mercado Pago
st.markdown("""
    <style>
    .stApp {
        background-color: #ededed;
        color: #333333;
    }
    .ml-card {
        background-color: #ffffff;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        padding: 14px;
        margin-bottom: 16px;
        border: 1px solid #e0e0e0;
    }
    .ml-title {
        font-size: 14px;
        font-weight: 600;
        color: #333;
        margin: 8px 0;
        height: 40px;
        overflow: hidden;
    }
    .ml-price {
        font-size: 22px;
        font-weight: 400;
        color: #333;
    }
    .ml-installments {
        font-size: 13px;
        color: #00a650;
        font-weight: 600;
    }
    .stButton>button {
        background-color: #3483fa;
        color: white;
        border-radius: 6px;
        font-weight: bold;
        border: none;
        height: 38px;
    }
    .stButton>button:hover {
        background-color: #2968c8;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Enlaces a tu Google Sheet "MUEBLES"
SHEET_ID = "1Jw1ZtYGdAx2BLB9yxgmbZ7F4yc4Pka32bIa2XtxtSHw"  # ID de tu planilla MUEBLES
GID = "0"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

# ⚠️ PEGA AQUÍ TU URL DE APPS SCRIPT DE LA PLANILLA MUEBLES
SCRIPT_URL_MUEBLES = "https://script.google.com/macros/s/TU_SCRIPT_MUEBLES/exec"

# --- PANEL LATERAL: AGREGAR NUEVO MUEBLE CON FOTO ---
with st.sidebar:
    st.markdown("<h2>➕ Registrar Nuevo Mueble</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:12px; color:#666;'>Sube la foto y carga los datos para actualizar el stock al instante.</p>", unsafe_allow_html=True)
    
    with st.form("form_nuevo_articulo", clear_on_submit=True):
        nombre_mueble = st.text_input("Nombre del Mueble")
        categoria_mueble = st.selectbox("Categoría", options=["LIVING", "COMEDOR", "DORMITORIO", "A.J GESTIÓN URBANA", "METALÚRGICA"])
        precio_contado = st.number_input("Precio Contado ($)", min_value=1.0, value=200000.0, step=5000.0)
        cantidad_stock = st.number_input("Cantidad en Stock", min_value=1, value=1, step=1)
        descripcion = st.text_area("Descripción / Detalles")
        
        cant_cuotas = st.selectbox("Cantidad de Cuotas", options=[3, 6, 9, 12], index=1)
        interes_est = st.slider("Recargo Financiero Estimado (%)", 0.0, 30.0, 10.0, 1.0)
        
        # Calcular precio financiado automáticamente
        precio_financiado = precio_contado * (1 + (interes_est / 100))
        
        # Subir foto real desde el celular o PC
        foto_file = st.file_uploader("Foto del Mueble", type=["jpg", "jpeg", "png"])
        
        btn_publicar = st.form_submit_button("💾 Guardar Mueble en la Nube", use_container_width=True)
        
        if btn_publicar:
            if not nombre_mueble.strip():
                st.error("⚠️ El nombre es obligatorio.")
            else:
                # Convertir imagen a Base64 para enviarla de forma segura por Apps Script
                img_base64 = ""
                mime_type = "image/jpeg"
                nombre_archivo = "mueble_default.jpg"
                
                if foto_file is not None:
                    img_bytes = foto_file.read()
                    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                    mime_type = foto_file.type
                    nombre_archivo = foto_file.name

                payload = {
                    "action": "agregar_mueble",
                    "nombre": nombre_mueble.strip(),
                    "precio": precio_contado,
                    "cantidad": cantidad_stock,
                    "categoria": categoria_mueble,
                    "descripcion": descripcion.strip(),
                    "precioFinanciado": round(precio_financiado, 2),
                    "cantCuotas": cant_cuotas,
                    "imagenBase64": img_base64,
                    "mimeType": mime_type,
                    "nombreArchivo": nombre_archivo
                }

                if "script.google.com" in SCRIPT_URL_MUEBLES:
                    try:
                        res = requests.post(SCRIPT_URL_MUEBLES, data=json.dumps(payload), timeout=25)
                        resultado = res.json()
                        if resultado.get("status") == "OK":
                            st.success("🎉 ¡Mueble guardado y foto subida a Google Drive!")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(f"Error del servidor: {resultado.get('message')}")
                    except Exception as e:
                        st.error(f"Error de conexión: {e}")
                else:
                    st.warning("⚠️ Configura la variable `SCRIPT_URL_MUEBLES` con tu Apps Script.")

# --- CUERPO PRINCIPAL: CATÁLOGO INTERNO DE VENTAS ---
st.markdown("<h2>🛍️ A&G VENTAS PRO - Stock Disponible</h2>", unsafe_allow_html=True)
busqueda = st.text_input("🔍 Buscar muebles en stock...", placeholder="Escribe el nombre del mueble...", label_visibility="collapsed")
st.markdown("<br>", unsafe_allow_html=True)

@st.cache_data(ttl=0)
def cargar_catalogo():
    try:
        df = pd.read_csv(CSV_URL, header=2)
        df.columns = [str(col).strip().upper() for col in df.columns]
        return df
    except Exception as e:
        return None

df_muebles = cargar_catalogo()

if df_muebles is not None and not df_muebles.empty:
    # Limpieza de columnas esperadas: ID, NOMBRE, PRECIO, CANTIDAD, CATEGORIA, DESCRIPCION, PRECIO FINANCIADO, CANT CUOTAS
    col_nombre = next((c for c in df_muebles.columns if "NOMBRE" in c), None)
    col_precio = next((c for c in df_muebles.columns if c == "PRECIO"), None)
    col_cat = next((c for c in df_muebles.columns if "CATEGORIA" in c), None)
    col_desc = next((c for c in df_muebles.columns if "DESCRIPCION" in c), None)
    col_pfin = next((c for c in df_muebles.columns if "FINANCIADO" in c), None)
    col_cuotas = next((c for c in df_muebles.columns if "CUOTAS" in c), None)

    if col_nombre:
        df_valid = df_muebles.dropna(subset=[col_nombre]).copy()
        
        # Filtro de búsqueda
        if busqueda:
            df_valid = df_valid[df_valid[col_nombre].astype(str).str.contains(busqueda, case=False, na=False)]

        cols = st.columns(3) # Grilla de 3 columnas estilo Mercado Libre
        
        for idx, row in df_valid.iterrows():
            col_actual = cols[idx % 3]
            
            nombre = str(row[col_nombre])
            precio = float(str(row[col_precio]).replace('$', '').replace('.', '').replace(',', '.')) if col_precio and pd.notna(row[col_precio]) else 0.0
            categoria = str(row[col_cat]) if col_cat and pd.notna(row[col_cat]) else "GENERAL"
            desc_completa = str(row[col_desc]) if col_desc and pd.notna(row[col_desc]) else ""
            
            # Extraer imagen y descripción limpia
            img_url = "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=600&q=80"
            desc_limpia = desc_completa
            if "[FOTO:" in desc_completa:
                partes = desc_completa.split("[FOTO:")
                desc_limpia = partes[0].strip()
                img_url = partes[1].replace("]", "").strip()

            p_fin = float(str(row[col_pfin]).replace('$', '').replace('.', '').replace(',', '.')) if col_pfin and pd.notna(row[col_pfin]) else precio
            n_cuotas = int(row[col_cuotas]) if col_cuotas and pd.notna(row[col_cuotas]) else 6
            valor_cuota = p_fin / n_cuotas if n_cuotas > 0 else precio

            with col_actual:
                st.markdown(f"""
                    <div class="ml-card">
                        <img src="{img_url}" style="width: 100%; height: 190px; object-fit: cover; border-radius: 4px;">
                        <span style="font-size:10px; font-weight:bold; background:#e6f0ff; color:#0073e6; padding:2px 6px; border-radius:3px; display:inline-block; margin-top:8px;">{categoria}</span>
                        <div class="ml-title">{nombre}</div>
                        <div style="font-size:11px; color:#666; margin-bottom:6px;">{desc_limpia}</div>
                        <div class="ml-price">$ {precio:,.2f}</div>
                        <div class="ml-installments">{n_cuotas} cuotas de $ {valor_cuota:,.2f}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Botón de WhatsApp integrado para el vendedor
                with st.expander("💬 Enviar Presupuesto WhatsApp"):
                    tel_wsp = st.text_input("Celular cliente (ej: 3764xxxxxx)", key=f"t_{idx}")
                    if st.button("🚀 Enviar Presupuesto", key=f"b_{idx}", use_container_width=True):
                        if not tel_wsp.strip():
                            st.warning("⚠️ Ingrese el número.")
                        else:
                            msg = f"¡Hola! 👋 Te enviamos la cotización desde *Mueblería A&G*:\n\n" \
                                  f"🪑 *{nombre}*\n" \
                                  f"📝 {desc_limpia}\n" \
                                  f"💰 *Contado:* ${precio:,.2f}\n" \
                                  f"💳 *Financiación:* {n_cuotas} cuotas de ${valor_cuota:,.2f}\n\n" \
                                  f"¿Coordinamos la seña o el envío?"
                            
                            link = f"https://api.whatsapp.com/send?phone=549{tel_wsp.strip()}&text={urllib.parse.quote(msg)}"
                            st.markdown(f'<meta http-equiv="refresh" content="0;url={link}">', unsafe_allow_html=True)
                            st.success("✅ ¡Abriendo WhatsApp!")
    else:
        st.info("📌 Tu tabla MUEBLES está vacía o se están cargando los primeros registros.")
else:
    st.info("📌 Todavía no hay datos cargados en la hoja 'MUEBLES'. Utiliza el panel izquierdo para dar de alta tu primer artículo.")
