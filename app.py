import streamlit as st
from PIL import Image, ImageDraw
import time
import numpy as np
import io  # <-- Nueva librería para manejar el buffer de descarga en memoria

# Importamos la lógica de Inteligencia Artificial desde nuestro backend (modelo.py)
from modelo import comprimir_imagen, rgb_a_hex

# Configuración de página
st.set_page_config(
    page_title="Equipo 2 - Compresión de Imágenes con K-Means",
    page_icon="🎨",
    layout="wide"
)

# --- BARRA LATERAL (Panel de Control) ---
st.sidebar.header("⚙️ Configuración")

# Selector de Tema (Modo Oscuro / Claro)
modo_oscuro = st.sidebar.toggle("Modo Oscuro 🌙", value=True)

# Variables dinámicas según el tema seleccionado
if modo_oscuro:
    bg_color = "#0f172a"
    text_color = "#f8fafc"
    card_bg = "#1e293b"
    border_color = "rgba(255, 255, 255, 0.15)"
else:
    bg_color = "#f1f5f9"
    text_color = "#0f172a"
    card_bg = "#ffffff"
    border_color = "rgba(0, 0, 0, 0.15)"

# Inyección de estilos CSS dinámicos
st.markdown(f"""
<style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, span {{
        color: {text_color} !important;
    }}
    .title-banner {{
        background: linear-gradient(90deg, #0284c7 0%, #6366f1 100%);
        padding: 20px;
        border-radius: 12px;
        color: #ffffff !important;
        text-align: center;
        margin-bottom: 25px;
    }}
    .title-banner h1, .title-banner h3 {{
        color: #ffffff !important;
    }}
    .color-card {{
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        color: #ffffff !important;
        font-weight: bold;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.9);
        border: 1px solid {border_color};
    }}
    div[data-testid="stMetric"] {{
        background-color: {card_bg};
        padding: 12px;
        border-radius: 8px;
        border: 1px solid {border_color};
    }}
</style>
""", unsafe_allow_html=True)

# Encabezado principal
st.markdown("""
<div class="title-banner">
    <h1>EQUIPO 2: Aprendizaje No Supervisado</h1>
    <h3>"El que descubre solo" — Compresión de Imágenes con K-Means</h3>
</div>
""", unsafe_allow_html=True)

# Explicación del funcionamiento
with st.expander("📖 ¿Por qué este modelo es Aprendizaje No Supervisado?", expanded=False):
    st.markdown("""
    * **Sin Etiquetas Previas:** La máquina recibe la imagen como píxeles sin clasificar.
    * **Descubrimiento Autónomo:** Agrupa los colores organizando los píxeles en un espacio tridimensional (RGB) según su cercanía matemática.
    * **Centroides (Colores Dominantes):** El algoritmo calcula por sí mismo los K puntos centrales que mejor representan los colores de la imagen.
    """)

# Función para generar una imagen de muestra en caso de no subir archivo
def crear_imagen_muestra():
    img = Image.new('RGB', (400, 400), color=(30, 41, 59))
    draw = ImageDraw.Draw(img)
    draw.ellipse([50, 50, 200, 200], fill=(239, 68, 68))
    draw.rectangle([180, 150, 350, 320], fill=(59, 130, 246))
    draw.polygon([(200, 50), (350, 80), (280, 220)], fill=(34, 197, 94))
    draw.ellipse([100, 220, 250, 370], fill=(234, 179, 8))
    return img

archivo_subido = st.sidebar.file_uploader(
    "1. Sube tu imagen (JPG, PNG):", 
    type=["jpg", "jpeg", "png", "webp"]
)

st.sidebar.subheader("2. Selecciona el número de colores (K):")

# Botones rápidos para valores típicos de K (4, 8, 16)
col_b1, col_b2, col_b3 = st.sidebar.columns(3)
k_preset = None
if col_b1.button("K = 4"): k_preset = 4
if col_b2.button("K = 8"): k_preset = 8
if col_b3.button("K = 16"): k_preset = 16

val_k_defecto = k_preset if k_preset else 8

k_seleccionado = st.sidebar.slider(
    "Valor de K (Clusters / Colores):",
    min_value=2,
    max_value=32,
    value=val_k_defecto,
    step=1,
    help="Valores pequeños aplanan la imagen; valores grandes la acercan a la original."
)

# Cargar la imagen elegida o la predeterminada
if archivo_subido is not None:
    imagen_original = Image.open(archivo_subido)
else:
    st.sidebar.info("💡 Mostrando imagen de muestra. Puedes subir cualquier foto arriba.")
    imagen_original = crear_imagen_muestra()

# --- PROCESAMIENTO EN EL BACKEND ---
inicio_tiempo = time.time()
with st.spinner(f"Ejecutando K-Means con K={k_seleccionado}..."):
    imagen_comprimida, centros_rgb, porcentajes, metricas = comprimir_imagen(
        imagen_original, 
        k=k_seleccionado
    )
tiempo_ejecucion = time.time() - inicio_tiempo

# --- VISUALIZACIÓN LADO A LADO ---
st.subheader("🖼️ Comparación Visual")

col_izq, col_der = st.columns(2)

with col_izq:
    st.markdown("### Imagen Original")
    st.image(imagen_original, use_container_width=True)
    st.caption(f"📐 Dimensiones: {metricas['dimensiones'][0]}x{metricas['dimensiones'][1]}px | 🎨 ~{metricas['colores_unicos_orig']:,} colores únicos")

with col_der:
    st.markdown(f"### Imagen Comprimida (K = {k_seleccionado})")
    st.image(imagen_comprimida, use_container_width=True)
    st.caption(f"⚡ Tiempo de cómputo: {tiempo_ejecucion:.2f} s | 🎨 Reducido a solo **{k_seleccionado}** colores exactos")
    
    # --- PREPARACIÓN DEL BOTÓN DE DESCARGA ---
    buffer_descarga = io.BytesIO()
    imagen_comprimida.save(buffer_descarga, format="PNG")
    bytes_imagen = buffer_descarga.getvalue()

    st.download_button(
        label=f"💾 Descargar Imagen Comprimida (K={k_seleccionado})",
        data=bytes_imagen,
        file_name=f"imagen_comprimida_k{k_seleccionado}.png",
        mime="image/png",
        use_container_width=True
    )

st.divider()

# --- PALETA DE COLORES ENCONTRADA ---
st.subheader("🎨 Paleta de Colores Dominantes Encontrada por K-Means")

cols_paleta = st.columns(min(k_seleccionado, 8))
for i, (rgb, pct) in enumerate(zip(centros_rgb, porcentajes)):
    hex_code = rgb_a_hex(rgb)
    col_idx = i % 8
    with cols_paleta[col_idx]:
        st.markdown(f"""
        <div class="color-card" style="background-color: {hex_code};">
            Grupo {i+1}<br>
            {hex_code}<br>
            <small>{pct:.1f}% del total</small>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# --- MÉTRICAS TÉCNICAS ---
st.subheader("📊 Datos del Modelo")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Colores Originales (Aprox)", f"{metricas['colores_unicos_orig']:,}")
m2.metric("Colores Objetivo (K)", f"{k_seleccionado}")
m3.metric("Inercia K-Means (SSE)", f"{metricas['inercia']:,.0f}")
m4.metric("Iteraciones de Convergencia", f"{metricas['iteraciones']}")