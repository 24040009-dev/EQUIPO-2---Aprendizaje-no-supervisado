# 🎨 EQUIPO 2 - Aprendizaje No Supervisado
## "El que descubre solo": Compresión de Imágenes a K Colores con K-Means

Este proyecto implementa un sistema de Inteligencia Artificial No Supervisada capaz de procesar cualquier imagen y cuantizar su paleta de colores a $K$ tonos dominantes utilizando el algoritmo **K-Means**.

---

### 👥 Integrantes del Equipo
* Integrante 1 Angel Rangel
* Integrante 2 Juan Reyna
* Integrante 3 Angel Verastegui 

---

### 🚀 ¿Cómo ejecutar este proyecto localmente?

#### 1. Clonar el repositorio y abrir en VS Code 
Abre tu terminal en windows o símbolo del sistema (CMD / PowerShell) y ejecuta:
```bash
git clone https://github.com/24040009-dev/EQUIPO-2---Aprendizaje-no-supervisado.git

cd EQUIPO-2---Aprendizaje-no-supervisado

python -m venv venv
.\venv\Scripts\activate

pip install -r requirements.txt

streamlit run app.py


For MAC
Crear el entorno virtual utilizando python3:
Bash
python3 -m venv venv
Activar el entorno virtual (sintaxis para macOS):
Bash
source venv/bin/activate
(Al activarlo correctamente, aparecerá (venv) al inicio de la línea de comandos en la terminal).
Instalar las librerías necesarias:
Bash
pip install -r requirements.txt
Lanzar la aplicación:
Bash
streamlit run app.py
Si al ejecutar python3 el sistema indica que tampoco lo encuentra, deberás instalar Python en la Mac (puedes descargarlo desde el sitio oficial de Python o mediante Homebrew con brew install python).
