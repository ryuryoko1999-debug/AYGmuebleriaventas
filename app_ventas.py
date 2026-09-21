import streamlit as st
import pandas as pd
import requests
import json
import base64

# Configuración de página en modo ancho (tipo E-commerce)
st.set_page_config(
    page_title="A&G Ventas Pro",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos visuales unificados estilo Mercado Libre sin botones extra
st.markdown("""
    <style>
    .stApp {
        background-color: #ededed;
        color: #333333;
    }
    .ml-card-link {
        text-decoration: none !important;
        color: inherit !important;
        display: block;
    }
    .ml-card {
        background-color: #ffffff;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        overflow: hidden;
        margin-bottom: 20px;
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .ml-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.15);
        border-color: #3483fa;
    }
    .ml-img {
        width: 100%;
        height: 190px;
        object-fit: cover;
        display: block;
    }
    .ml-content {
        padding: 14px;
    }
    .ml-title {
        font-size: 14px;
        font-weight: 600;
        color: #333;
        margin: 6px 0;
        height: 38px;
        overflow: hidden;
    }
    .price-old {
        font-size: 12px;
        color: #999;
        text-decoration: line-through;
        margin-bottom: -4px;
    }
    .ml-price {
        font-size: 20px;
        font-weight: 400;
        color: #333;
    }
    .ml-installments {
        font-size: 12px;
        color: #00a650;
        font-weight: 600;
        margin-top: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURACIÓN DE ACCESO A GOOGLE SHEETS ---
SHEET_ID = "1Jw1ZtYGdAx2BLB9yxgmbZ7F4yc4Pka32bIa2XtxtSHw"
GID = "0"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

# ⚠️ PEGA TU URL DE APPS SCRIPT AQUÍ (la que termina en /exec)
SCRIPT_URL_MUEBLES = "https://script.google.com/macros/s/AKfycbw3OPwzlrzvi-2zkX_qUyQG_xK3AltPc9J_iEHWkFwskoyfAeZBg_DvRqnMLokCdEY/exec"

# --- PANEL LATERAL: AGREGAR NUEVO MUEBLE ---
with st.sidebar:
    st.markdown("<h2>➕ Registrar Nuevo Mueble</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:12px; color:#666;'>Crea una carpeta exclusiva en Drive con múltiples fotos para este artículo.</p>", unsafe_allow_html=True)
    
    with st.form("form_nuevo_articulo", clear_on_submit=True):
        nombre_mueble = st.text_input("Nombre del Mueble")
        categoria_mueble = st.selectbox("Categoría", options=["LIVING", "COMEDOR", "DORMITORIO", "A.J GESTIÓN URBANA", "METALÚRGICA"])
        precio_contado = st.number_input("Precio Contado ($)", min_value=1.0, value=200000.0, step=5000.0)
        cantidad_stock = st.number_input("Cantidad en Stock", min_value=1, value=1, step=1)
        descripcion = st.text_area("Descripción Detallada / Medidas / Materiales")
        
        cant_cuotas = st.selectbox("Cantidad de Cuotas", options=[3, 6, 9, 12], index=1)
        interes_est = st.slider("Recargo Financiero Estimado (%)", 0.0, 30.0, 10.0, 1.0)
        
        precio_financiado = precio_contado * (1 + (interes_est / 100))
        
        fotos_files = st.file_uploader("Fotos del Mueble (La 1era será la portada)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        
        btn_publicar = st.form_submit_button("💾 Crear Carpeta y Publicar", use_container_width=True)
        
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
                            st.success("🎉 ¡Carpeta de Drive creada y mueble guardado!")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(f"Error del servidor: {resultado.get('message')}")
                    except Exception as e:
                        st.error(f"Error de conexión: {e}")
                else:
                    st.warning("⚠️ Configura la variable `SCRIPT_URL_MUEBLES`.")

# --- CARGAR CATÁLOGO ---
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

# --- DETECTAR SI SE SELECCIONÓ UN PRODUCTO MEDIANTE LA URL ---
selected_prod_id = st.query_params.get("prod_id", None)

if df_muebles is not None and not df_muebles.empty:
    col_nombre = next((c for c in df_muebles.columns if "NOMBRE" in c), None)
    col_precio = next((c for c in df_muebles.columns if c == "PRECIO" or "PRECIO" in c), None)
    col_cat = next((c for c in df_muebles.columns if "CATEGORIA" in c), None)
    col_desc = next((c for c in df_muebles.columns if "DESCRIPCION" in c), None)
    col_pfin = next((c for c in df_muebles.columns if "FINANCIADO" in c), None)
    col_cuotas = next((c for c in df_muebles.columns if "CUOTAS" in c), None)

    if col_nombre:
        df_valid = df_muebles.dropna(subset=[col_nombre]).copy()
        df_valid = df_valid[~df_valid[col_nombre].astype(str).str.upper().isin(['NAN', 'NONE', '', 'NOMBRE'])].reset_index(drop=True)

        # Si el usuario hizo clic en una tarjeta, mostramos la VISTA DETALLADA
        if selected_prod_id is not None:
            try:
                idx_sel = int(selected_prod_id)
                if 0 <= idx_sel < len(df_valid):
                    row_sel = df_valid.iloc[idx_sel]
                    nombre = str(row_sel[col_nombre])
                    categoria = str(row_sel[col_cat]) if col_cat and pd.notna(row_sel[col_cat]) else "GENERAL"
                    desc_completa = str(row_sel[col_desc]) if col_desc and pd.notna(row_sel[col_desc]) else ""
                    
                    raw_precio = str(row_sel[col_precio]).replace('$', '').replace('.', '').replace(',', '.').strip() if col_precio and pd.notna(row_sel[col_precio]) else "0"
                    try:
                        precio = float(raw_precio)
                    except:
                        precio = 0.0

                    img_url = "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=600&q=80"
                    url_drive_carpeta = "https://drive.google.com"
                    desc_limpia = desc_completa

                    if "[FOTO:" in desc_completa:
                        partes = desc_completa.split("[FOTO:")
                        desc_limpia = partes[0].strip()
                        resto = partes[1]
                        if "[DRIVE_CARPETA:" in resto:
                            subpartes = resto.split("[DRIVE_CARPETA:")
                            img_url = subpartes[0].replace("]", "").strip()
                            url_drive_carpeta = subpartes[1].replace("]", "").strip()
                        else:
                            img_url = resto.replace("]", "").strip()
                    elif "[DRIVE_CARPETA:" in desc_completa:
                        partes = desc_completa.split("[DRIVE_CARPETA:")
                        desc_limpia = partes[0].strip()
                        url_drive_carpeta = partes[1].replace("]", "").strip()

                    raw_pfin = str(row_sel[col_pfin]).replace('$', '').replace('.', '').replace(',', '.').strip() if col_pfin and pd.notna(row_sel[col_pfin]) else str(precio)
                    try:
                        p_fin = float(raw_pfin)
                    except:
                        p_fin = precio

                    raw_cuotas = str(row_sel[col_cuotas]).strip() if col_cuotas and pd.notna(row_sel[col_cuotas]) else "6"
                    try:
                        n_cuotas = int(float(raw_cuotas))
                    except:
                        n_cuotas = 6

                    valor_cuota = p_fin / n_cuotas if n_cuotas > 0 else precio
                    precio_anterior = precio * 1.30

                    # Botón para regresar al catálogo
                    if st.button("⬅️ Volver al Catálogo General"):
                        st.query_params.clear()
                        st.rerun()

                    st.markdown(f"<h1>{nombre}</h1>", unsafe_allow_html=True)
                    st.markdown(f"<span style='background:#e6f0ff; color:#0073e6; padding:4px 8px; border-radius:4px; font-weight:bold;'>{categoria}</span>", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

                    col_img, col_info = st.columns([1.2, 1])

                    with col_img:
                        st.markdown(f'<img src="{img_url}" style="width: 100%; max-height: 400px; object-fit: contain; border-radius: 8px; border: 1px solid #ddd; background: #fff; padding: 10px;">', unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)

                        st.markdown(f"""
                            <a href="{url_drive_carpeta}" target="_blank" style="display: block; width: 100%; background-color: #0073e6; color: white; padding: 12px 0; text-align: center; border-radius: 6px; font-weight: bold; text-decoration: none; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                📁 Abrir Carpeta Exclusiva en Google Drive (Ver todas las fotos)
                            </a>
                        """, unsafe_allow_html=True)

                    with col_info:
                        st.markdown(f"""
                            <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #ddd;">
                                <h3 style="margin-top:0; color:#333;">Precio Contado</h3>
                                <div class="price-old">$ {precio_anterior:,.2f}</div>
                                <div style="font-size: 32px; font-weight: bold; color: #333;">$ {precio:,.2f} <span style="font-size:14px; background:#e5ffe5; color:#00a650; padding:2px 6px; border-radius:4px;">30% OFF</span></div>
                                <hr style="margin: 15px 0;">
                                <h4 style="color: #00a650; margin:0;">Financiación Disponible</h4>
                                <div style="font-size: 18px; font-weight: bold; color: #00a650; margin-top:5px;">
                                    {n_cuotas} cuotas de $ {valor_cuota:,.2f}
                                </div>
                                <div style="font-size: 12px; color: #666; margin-top:3px;">Total financiado: $ {p_fin:,.2f}</div>
                            </div>
                        """, unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("### 📝 Descripción Completa y Especificaciones")
                    st.markdown(f"""
                        <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #ddd; line-height: 1.6;">
                            {desc_limpia}
                        </div>
                    """, unsafe_allow_html=True)

            except Exception as e:
                st.error("Ocurrió un error al cargar los detalles del producto.")
                if st.button("Volver"):
                    st.query_params.clear()
                    st.rerun()

        else:
            # --- VISTA GENERAL: CATÁLOGO DE TARJETAS NATIVAS Y CLICKAIBLES ---
            st.markdown("<h2>🛍️ A&G VENTAS PRO - Catálogo Interactivo</h2>", unsafe_allow_html=True)
            busqueda = st.text_input("🔍 Buscar muebles en stock (ej: placar, mesa, etc.)...", placeholder="Escribe para filtrar...", label_visibility="collapsed")
            st.markdown("<br>", unsafe_allow_html=True)

            if busqueda:
                df_valid = df_valid[df_valid[col_nombre].astype(str).str.contains(busqueda, case=False, na=False)].reset_index(drop=True)

            if df_valid.empty:
                st.info("📌 No se encontraron muebles que coincidan con la búsqueda.")
            else:
                cols = st.columns(3)

                for idx, row in df_valid.iterrows():
                    col_actual = cols[idx % 3]

                    nombre = str(row[col_nombre])

                    raw_precio = str(row[col_precio]).replace('$', '').replace('.', '').replace(',', '.').strip() if col_precio and pd.notna(row[col_precio]) else "0"
                    try:
                        precio = float(raw_precio)
                    except:
                        precio = 0.0

                    categoria = str(row[col_cat]) if col_cat and pd.notna(row[col_cat]) else "GENERAL"
                    desc_completa = str(row[col_desc]) if col_desc and pd.notna(row[col_desc]) else ""

                    img_url = "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=600&q=80"
                    if "[FOTO:" in desc_completa:
                        partes = desc_completa.split("[FOTO:")
                        resto = partes[1]
                        if "[DRIVE_CARPETA:" in resto:
                            img_url = resto.split("[DRIVE_CARPETA:")[0].replace("]", "").strip()
                        else:
                            img_url = resto.replace("]", "").strip()

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
                    precio_anterior = precio * 1.30

                    with col_actual:
                        # Toda la tarjeta es un único elemento interactivo mediante enlace a la vista de detalle
                        st.markdown(f"""
                            <a href="?prod_id={idx}" target="_self" class="ml-card-link">
                                <div class="ml-card">
                                    <img src="{img_url}" class="ml-img">
                                    <div class="ml-content">
                                        <span style="font-size:10px; font-weight:bold; background:#e6f0ff; color:#0073e6; padding:2px 6px; border-radius:3px; display:inline-block; margin-bottom:4px;">{categoria}</span>
                                        <div class="ml-title">{nombre}</div>
                                        <div class="price-old">$ {precio_anterior:,.2f}</div>
                                        <div class="ml-price">$ {precio:,.2f}</div>
                                        <div class="ml-installments">{n_cuotas} cuotas de $ {valor_cuota:,.2f}</div>
                                    </div>
                                </div>
                            </a>
                        """, unsafe_allow_html=True)
    else:
        st.error("⚠️ No se encontró la columna 'NOMBRE' en la planilla.")
else:
    st.info("📌 Todavía no hay datos cargados en la hoja 'MUEBLES'. Utiliza el panel izquierdo para dar de alta tu primer artículo.")
