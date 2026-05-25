# Archivo: ExploradorProteinas.py
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai

st.set_page_config(page_title="Visualizador", layout="wide")

st.title("🧬 Explorador de Proteínas Interactivo")

# --- VENTANA FLOTANTE DE INSTRUCCIONES ---
@st.dialog("📖 Cómo usar esta Aplicación")
def mostrar_instrucciones():
    st.markdown("""
    ### 👋 ¡Bienvenido al Explorador de Proteínas!
    Esta herramienta interactiva te permite explorar la arquitectura molecular tridimensional de proteínas esenciales para la vida y comprender su plegamiento con ayuda de IA.
    
    ### 🎮 ¿Cómo interactuar con la proteína en 3D?
    * **Rotar:** Haz clic izquierdo dentro del recuadro de la proteína y arrastra el cursor en cualquier dirección.
    * **Zoom:** Usa la rueda de desplazamiento de tu mouse (scroll) o desliza dos dedos en el trackpad hacia arriba o hacia abajo dentro del visualizador.
    * **Mover (Pan):** Mantén presionada la tecla `Shift` (Mayús) mientras haces clic izquierdo y arrastras.
    
    ### 🧠 El Experto con IA
    Selecciona un nivel de plegamiento en la barra lateral. Gemini analizará la estructura visualizada y te explicará a la derecha su relevancia biológica.
    """)

# --- BARRA LATERAL ---
st.sidebar.title("Configuración")

# Botón destacado de instrucciones
if st.sidebar.button("❓ Ver Instrucciones de Uso", use_container_width=True):
    mostrar_instrucciones()

st.sidebar.markdown("---")

api_key = st.sidebar.text_input("Introduce tu Gemini API Key:", type="password")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.sidebar.warning("Por favor, introduce tu API Key para activar el análisis con IA.")

# Catálogo expandido de proteínas (Diccionario Nombre: Código PDB)
proteinas = {
    "Insulina (Metabolismo)": "1TRZ", 
    "Hemoglobina (Transporte de Oxígeno)": "1A3N", 
    "Colágeno (Estructura de la piel)": "1BKV",
    "Queratina (Cabello y Uñas)": "1CO4",
    "Mioglobina (Reserva de Oxígeno muscular)": "1MBN",
    "Proteína Spike (Coronavirus)": "6VXX",
    "Anticuerpo Inmunoglobulina G": "1IGY"
}

nombre = st.sidebar.selectbox("Proteína a estudiar:", list(proteinas.keys()))
pdb_id = proteinas[nombre]

# Selector de Nivel
nivel = st.sidebar.radio(
    "Nivel de Plegamiento:", 
    ["Primaria (Cadena)", "Secundaria (Cintas)", "Terciaria (3D Completa)"]
)

if "Primaria" in nivel:
    estilo_visual = "stick"
elif "Secundaria" in nivel:
    estilo_visual = "cartoon"
else:
    estilo_visual = "sphere"

st.subheader(f"🔍 Análisis interactivo: {nombre}")

# --- DISEÑO DE COLUMNAS ---
col1, col2 = st.columns([4, 3])

with col1:
    st.markdown(f"**Visualización: {nivel}**")
    # Renderizador molecular (Fijo en pantalla)
    html_code = f"""
    <div style="height: 450px; width: 100%; position: relative;" 
         class='viewer_3Dmoljs' data-pdb='{pdb_id}' 
         data-backgroundcolor='0xf8f9fa' 
         data-style='{estilo_visual}:{{colorscheme:"spectrum"}}'></div>
    <script src="https://3dmol.org/build/3Dmol-min.js"></script>
    """
    components.html(html_code, height=460)

with col2:
    st.markdown("### 🧠 Explicación del Experto")
    
    # VENTANA CON SCROLL PROPIO (Contenedor con altura fija)
    with st.container(height=430):
        if api_key:
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                prompt = (
                    f"Actúa como un bioquímico experto y docente didáctico. "
                    f"Explica de forma sencilla, clara y dinámica cómo se comporta la proteína '{nombre}' "
                    f"específicamente en su estructura o nivel '{nivel}'. "
                    f"Enfócate en cómo este nivel de plegamiento afecta su función biológica."
                )
                
                # Efecto visual de carga local dentro del contenedor
                with st.spinner("Analizando enlaces moleculares..."):
                    respuesta = model.generate_content(prompt)
                st.write(respuesta.text)
                
            except Exception as e:
                st.error(f"Error de conexión: {e}")
        else:
            st.info("Coloca tu API Key en la barra lateral izquierda para que el experto empiece el análisis de plegamiento.")
