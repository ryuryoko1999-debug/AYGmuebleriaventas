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

# Estilos visuales limpios estilo Mercado Libre
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

# --- CONFIGURACIÓN DE ACCESO A GOOGLE SHEETS ---
SHEET_ID = "1Jw1ZtYGdAx2BLB9yxgmbZ7F4yc4Pka32bIa2XtxtSHw"
GID = "0"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

# ⚠️ PEGA TU URL DE APPS SCRIPT AQUí (la que termina en /exec)
SCRIPT_URL_MUEBLES = "https://script.google.com/macros/s/AKfycbw3OPwzlrzvi-2zkX_qUyQG_xK3AltPc9J_iEHWkFwskoyfAeZBg_DvRqnMLokCdEY/exec"

# --- PANEL LATERAL: AGREGAR NUEVO MUEBLE CON FOTOS MÚLTIPLES ---
with st.sidebar:
    st.markdown("<h2>➕ Registrar Nuevo Mueble</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:12px; color:#666;'>Sube una o varias fotos. El sistema creará una carpeta exclusiva en tu Drive.</p>", unsafe_allow_html=True)
    
    with st.form("form_nuevo_articulo", clear_on_submit=True):
        nombre_mueble = st.text_input("Nombre del Mueble")
        categoria_mueble = st.selectbox("Categoría", options=["LIVING", "COMEDOR", "DORMITORIO", "A.J GESTIÓN URBANA", "METALÚRGICA"])
        precio_contado = st.number_input("Precio Contado ($)", min_value=1.0, value=200000.0, step=5000.0)
        cantidad_stock = st.number_input("Cantidad en Stock", min_value=1, value=1, step=1)
        descripcion = st.text_area("Descripción / Detalles")
        
        cant_cuotas = st.selectbox("Cantidad de Cuotas", options=[3, 6, 9, 12], index=1)
        interes_est = st.slider("Recargo Financiero Estimado (%)", 0.0, 30.0, 10.0, 1.0)
        
        precio_financiado = precio_contado * (1 + (interes_est / 100))
        
        # Selector múltiple de archivos de imagen
        fotos_files = st.file_uploader("Seleccionar Fotos del Mueble (puedes subir varias)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        
        btn_publicar = st.form_submit_button("💾 Crear Carpeta y Guardar en Nube", use_container_width=True)
        
        if btn_publicar:
            if not nombre_mueble.strip():
                st.error("⚠️ El nombre es obligatorio.")
            else:
                lista_imagenes = []
                if fotos_files:
                    for f in fotos_files:
                        img_bytes = f.read()
                        b64_str = base64.b64encode(img_bytes).decode('utf-8')
                        lista_imagenes.append({
                            "base64": b64_str,
                            "mimeType": f.type,
                            "nombre": f.name
                        })

                payload = {
                    "action": "agregar_mueble",
                    "nombre": nombre_mueble.strip(),
                    "precio": precio_contado,
                    "cantidad": cantidad_stock,
                    "categoria": categoria_mueble,
                    "descripcion": descripcion.strip(),
                    "precioFinanciado": round(precio_financiado, 2),
                    "cantCuotas": cant_cuotas,
                    "imagenes": lista_imagenes
                }

                if "script.google.com" in SCRIPT_URL_MUEBLES:
                    try:
                        res = requests.post(SCRIPT_URL_MUEBLES, data=json.dumps(payload), timeout=35)
                        resultado = res.json()
                        if resultado.get("status") == "OK":
                            st.success("🎉 ¡Carpeta creada en Drive con sus fotos y mueble guardado!")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(f"Error del servidor: {resultado.get('message')}")
                    except Exception as e:
                        st.error(f"Error de conexión: {e}")
                else:
                    st.warning("⚠️ Debes configurar la variable `SCRIPT_URL_MUEBLES` con tu enlace real de Apps Script.")

# --- CUERPO PRINCIPAL: CATÁLOGO INTERNO DE VENTAS ---
st.markdown("<h2>🛍️ A&G VENTAS PRO - Stock Disponible</h2>", unsafe_allow_html=True)
busqueda = st.text_input("🔍 Buscar muebles en stock (ej: placar, mesa, etc.)...", placeholder="Escribe para filtrar...", label_visibility="collapsed")
st.markdown("<br>", unsafe_allow_html=True)

@st.cache_data(ttl=0)
def cargar_catalogo():
    try:
        df_raw = pd.read_csv(CSV_URL, header=None)
        
        header_row_idx = None
        for idx, row in df_raw.iterrows():
            row_str = str(row.values).upper()
            if "NOMBRE" in row_str and "PRECIO" in row_str:
                header_row_idx = idx
                break
        
        if header_row_idx is not None:
            df = pd.read_csv(CSV_URL, header=header_row_idx)
            df.columns = [str(c).strip().upper() for c in df.columns]
            return df
        else:
            df = pd.read_csv(CSV_URL, header=0)
            df.columns = [str(c).strip().upper() for c in df.columns]
            return df
    except Exception as e:
        st.error(f"Error leyendo la planilla: {e}")
        return None

df_muebles = cargar_catalogo()

if df_muebles is not None and not df_muebles.empty:
    col_nombre = next((c for c in df_muebles.columns if "NOMBRE" in c), None)
    col_precio = next((c for c in df_muebles.columns if c == "PRECIO" or "PRECIO" in c), None)
    col_cat = next((c for c in df_muebles.columns if "CATEGORIA" in c), None)
    col_desc = next((c for c in df_muebles.columns if "DESCRIPCION" in c), None)
    col_pfin = next((c for c in df_muebles.columns if "FINANCIADO" in c), None)
    col_cuotas = next((c for c in df_muebles.columns if "CUOTAS" in c), None)

    if col_nombre:
        df_valid = df_muebles.dropna(subset=[col_nombre]).copy()
        df_valid = df_valid[~df_valid[col_nombre].astype(str).str.upper().isin(['NAN', 'NONE', '', 'NOMBRE'])]

        if busqueda:
            df_valid = df_valid[df_valid[col_nombre].astype(str).str.contains(busqueda, case=False, na=False)]

        if df_valid.empty:
            st.info("📌 No se encontraron muebles que coincidan con la búsqueda.")
        else:
            cols = st.columns(3)
            
            for idx, row in df_valid.reset_index(drop=True).iterrows():
                col_actual = cols[idx % 3]
                
                nombre = str(row[col_nombre])
                
                raw_precio = str(row[col_precio]).replace('$', '').replace('.', '').replace(',', '.').strip() if col_precio and pd.notna(row[col_precio]) else "0"
                try:
                    precio = float(raw_precio)
                except:
                    precio = 0.0

                categoria = str(row[col_cat]) if col_cat and pd.notna(row[col_cat]) else "GENERAL"
                desc_completa = str(row[col_desc]) if col_desc and pd.notna(row[col_desc]) else ""
                
                # Extracción de URL de la carpeta de Drive o imagen por defecto
                url_drive_mueble = "https://drive.google.com"
                desc_limpia = desc_completa
                if "[DRIVE_CARPETA:" in desc_completa:
                    partes = desc_completa.split("[DRIVE_CARPETA:")
                    desc_limpia = partes[0].strip()
                    url_drive_mueble = partes[1].replace("]", "").strip()
                elif "[FOTO:" in desc_completa:
                    # Compatibilidad con registros anteriores
                    partes = desc_completa.split("[FOTO:")
                    desc_limpia = partes[0].strip()
                    url_drive_mueble = partes[1].replace("]", "").strip()

                raw_pfin = str(row[col_pfin]).replace('$', '').replace('.', '').replace(',', '.').strip() if col_pfin and pd.notna(row[col_pfin]) else str(precio)
                try:
                    p_fin = float(raw_pfin)
                except:
                    p_fin = precio

                raw_cuotas = str(row[col_cuotas]).strip() if col_cuotas and pd.notna(row[col_cuotas]) else "6"
                try:
                    n_cuotas = int(float(raw_cuotas))
                except:
                    n_cuotas = 6

                valor_cuota = p_fin / n_cuotas if n_cuotas > 0 else precio

                with col_actual:
                    st.markdown(f"""
                        <div class="ml-card">
                            <span style="font-size:10px; font-weight:bold; background:#e6f0ff; color:#0073e6; padding:2px 6px; border-radius:3px; display:inline-block; margin-bottom:4px;">{categoria}</span>
                            <div class="ml-title">{nombre}</div>
                            <div style="font-size:11px; color:#666; margin-bottom:6px; height:35px; overflow:hidden;">{desc_limpia}</div>
                            <div class="ml-price">$ {precio:,.2f}</div>
                            <div class="ml-installments">{n_cuotas} cuotas de $ {valor_cuota:,.2f}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Botón directo para abrir la carpeta exclusiva de Google Drive del mueble
                    st.markdown(f"""
                        <a href="{url_drive_mueble}" target="_blank" style="display: block; width: 100%; background-color: #0073e6; color: white; padding: 10px 0; text-align: center; border-radius: 6px; font-weight: bold; text-decoration: none; margin-top: -8px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            📁 Abrir Carpeta Google Drive (Fotos)
                        </a>
                    """, unsafe_allow_html=True)
    else:
        st.error("⚠️ No se encontró la columna 'NOMBRE' en la planilla.")
else:
    st.info("📌 Todavía no hay datos cargados en la hoja 'MUEBLES'. Utiliza el panel izquierdo para dar de alta tu primer artículo.")
