import streamlit as st
from PIL import Image, ImageDraw
import time
import numpy as np

# Importamos la lógica de Inteligencia Artificial desde nuestro backend (modelo.py)
from modelo import comprimir_imagen, rgb_a_hex

# Configuración de página
st.set_page_config(
    page_title="Equipo 2 - Compresión de Imágenes con K-Means",
    page_icon="🎨",
    layout="wide"
)

# Estilos CSS personalizados para mejorar el diseño
st.markdown("""
<style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .title-banner {
        background: linear-gradient(90deg, #0284c7 0%, #6366f1 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
    }
    .color-card {
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        color: white;
        font-weight: bold;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
        border: 1px solid rgba(255,255,255,0.2);
    }
    .metric-box {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #38bdf8;
    }
</style>
""", unsafe_allow_html=True)

# Encabezado principal
st.markdown("""
<div class="title-banner">
    <h1>🧠 EQUIPO 2: Aprendizaje No Supervisado</h1>
    <h3>"El que descubre solo" — Compresión de Imágenes con K-Means</h3>
</div>
""", unsafe_allow_html=True)

# Explicación teórica inicial
with st.expander("📖 ¿Por qué este modelo es Aprendizaje No Supervisado? (Da clic aquí)", expanded=False):
    st.markdown("""
    * **Sin Etiquetas Previa:** La máquina recibe millones de píxeles sin saber qué representan (no sabe si es "cielo", "piel" o "pasto").
    * **Descubrimiento Autónomo:** Agrupa los colores de la imagen organizando los píxeles en un espacio tridimensional $(R, G, B)$ según su cercanía matemática (Distancia Euclidiana).
    * **Centroides (Colores Dominantes):** El algoritmo calcula por sí mismo los $K$ puntos centrales que mejor representan todos los colores de la imagen original.
    """)

# Función para generar una imagen de muestra en caso de no subir archivo
def crear_imagen_muestra():
    img = Image.new('RGB', (400, 400), color=(30, 41, 59))
    draw = ImageDraw.Draw(img)
    # Dibujar formas coloridas para probar K-Means
    draw.ellipse([50, 50, 200, 200], fill=(239, 68, 68))    # Rojo
    draw.rectangle([180, 150, 350, 320], fill=(59, 130, 246)) # Azul
    draw.polygon([(200, 50), (350, 80), (280, 220)], fill=(34, 197, 94)) # Verde
    draw.ellipse([100, 220, 250, 370], fill=(234, 179, 8))   # Amarillo
    return img

# --- BARRA LATERAL (Panel de Control) ---
st.sidebar.header("⚙️ Configuración del Modelo")

archivo_subido = st.sidebar.file_uploader(
    "1. Sube tu imagen (JPG, PNG):", 
    type=["jpg", "jpeg", "png", "webp"]
)

# Control deslizante (Slider) para seleccionar K
st.sidebar.subheader("2. Selecciona el número de colores (K):")

# Botones rápidos para valores típicos de K exigidos en la rúbrica
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
with st.spinner(f"Entrenando K-Means con K={k_seleccionado}..."):
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
    st.image(imagen_original, use_column_width=True)
    st.caption(f"📐 Dimensiones: {metricas['dimensiones'][0]}x{metricas['dimensiones'][1]}px | 🎨 ~{metricas['colores_unicos_orig']:,} colores únicos")

with col_der:
    st.markdown(f"### Imagen Comprimida ($K = {k_seleccionado}$)")
    st.image(imagen_comprimida, use_column_width=True)
    st.caption(f"⚡ Tiempo de cómputo: {tiempo_ejecucion:.2f} s | 🎨 Reducido a solo **{k_seleccionado}** colores exactos")

st.divider()

# --- PALETA DE COLORES ENCONTRADA ---
st.subheader("🎨 Paleta de Colores Dominantes Encontrada por K-Means")
st.write("El algoritmo encontró de forma autónoma estos colores representativos (centroides):")

# Mostrar las tarjetas de color con código HEX y % de píxeles
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

# --- MÉTRICAS Y EXPLICACIÓN PARA DEFENDER EN CLASE ---
st.subheader("📊 Análisis Técnico y Preguntas de Defensa")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Colores Originales (Aprox)", f"{metricas['colores_unicos_orig']:,}")
m2.metric("Colores Objetivo (K)", f"{k_seleccionado}")
m3.metric("Inercia K-Means (SSE)", f"{metricas['inercia']:,.0f}")
m4.metric("Iteraciones de Convergencia", f"{metricas['iteraciones']}")

with st.expander("🎓 Preguntas clave para defender este proyecto con el profesor", expanded=True):
    st.markdown(f"""
    **1. ¿Qué representan los grupos/clusters encontrados?**
    * Cada grupo representa una **región de color dominante** en el espacio tridimensional RGB. 
    * Por ejemplo, si subes una foto de un paisaje, K-Means agrupa todos los tonos azulados (cielo, agua) en un único centroide promedio, los verdes (árboles, pasto) en otro, etc.

    **2. ¿Qué señal confirma que el sistema funciona correctamente?**
    * **Con $K$ pequeño ($K=2, 4$):** La imagen se ve "aplanada", con bordes marcados de tono plano y pérdida drástica de detalles (efecto cartelización o posterización).
    * **Con $K$ grande ($K=16, 32$):** La imagen comprimida es casi indistinguible visualmente de la original, pero usando una fracción muy pequeña de colores.

    **3. ¿Cómo calcula K-Means los colores sin supervisión?**
    * Utiliza la **distancia euclidiana** en 3D entre el valor $(R, G, B)$ de cada píxel y las $K$ posiciones iniciales.
    * Mueve iterativamente los $K$ centroides al promedio geométrico de los píxeles asignados a cada uno, hasta que los centroides dejan de moverse (convergencia alcanzada en {metricas['iteraciones']} iteraciones).
    """)