import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

def comprimir_imagen(imagen_pil, k=8, max_pixels=600):
    """
    Comprime una imagen cuantizando sus colores con K-Means (Aprendizaje No Supervisado).
    
    Parámetros:
        imagen_pil (PIL.Image): Imagen recibida del frontend.
        k (int): Número de centroides / colores a descubrir.
        max_pixels (int): Dimensión máxima para mantener velocidad en imágenes muy grandes.
        
    Retorna:
        imagen_comprimida (PIL.Image): Imagen reconstruida con solo K colores.
        centros_rgb (np.ndarray): Matriz de colores de los centroides en RGB.
        porcentajes (np.ndarray): % de píxeles asignados a cada color.
        metricas (dict): Datos técnicos (Inercia, colores originales estimadamente, etc.).
    """
    # 1. Asegurar formato RGB
    imagen_rgb = imagen_pil.convert('RGB')
    w_orig, h_orig = imagen_rgb.size
    
    # 2. Redimensionar temporalmente para optimizar la velocidad de cálculo
    ratio = min(1.0, max_pixels / max(w_orig, h_orig))
    if ratio < 1.0:
        w_proc, h_proc = int(w_orig * ratio), int(h_orig * ratio)
        img_proc = imagen_rgb.resize((w_proc, h_proc), Image.Resampling.LANCZOS)
    else:
        img_proc = imagen_rgb

    # 3. Convertir la imagen a un arreglo de píxeles
    # De forma (Alto, Ancho, 3) a una matriz de (Alto x Ancho, 3) -> Puntos en espacio 3D (R, G, B)
    img_np = np.array(img_proc)
    h, w, c = img_np.shape
    pixeles = img_np.reshape((-1, 3))
    
    # Estimación de colores únicos originales
    colores_unicos_orig = len(np.unique(pixeles, axis=0))
    
    # 4. APRENDIZAJE NO SUPERVISADO: Entrenar el modelo K-Means
    # Descubre solo los K grupos (centroides) en el espacio de color RGB
    kmeans = KMeans(
        n_clusters=k, 
        init='k-means++', 
        n_init=5, 
        max_iter=300, 
        random_state=42
    )
    
    # fit_predict asigna cada píxel al centroide más cercano
    labels = kmeans.fit_predict(pixeles)
    
    # 5. Obtener los centroides (colores dominantes descubiertos)
    centros_rgb = np.clip(kmeans.cluster_centers_, 0, 255).astype(np.uint8)
    
    # 6. Reconstruir la imagen reemplazando cada píxel por el color de su centroide
    pixeles_comprimidos = centros_rgb[labels]
    img_comprimida_np = pixeles_comprimidos.reshape((h, w, c))
    imagen_comprimida = Image.fromarray(img_comprimida_np)
    
    # Si redimensionamos, restauramos la dimensión original para mostrar
    if ratio < 1.0:
        imagen_comprimida = imagen_comprimida.resize((w_orig, h_orig), Image.Resampling.NEAREST)
        
    # 7. Calcular porcentaje de presencia de cada color en la imagen
    cuentas = np.bincount(labels, minlength=k)
    porcentajes = (cuentas / len(labels)) * 100
    
    # Ordenar paleta de mayor a menor frecuencia de aparición
    orden = np.argsort(-porcentajes)
    centros_rgb = centros_rgb[orden]
    porcentajes = porcentajes[orden]
    
    metricas = {
        'inercia': float(kmeans.inertia_),
        'colores_unicos_orig': colores_unicos_orig,
        'dimensiones': (w_orig, h_orig),
        'iteraciones': kmeans.n_iter_
    }
    
    return imagen_comprimida, centros_rgb, porcentajes, metricas


def rgb_a_hex(rgb):
    """Convierte una tupla/arreglo RGB [R, G, B] a código HEX (#RRGGBB)."""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}".upper()