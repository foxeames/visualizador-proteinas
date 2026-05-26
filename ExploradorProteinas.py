# Archivo definitivo: ExploradorProteinas.py
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai

# Configuración de página limpia y profesional
st.set_page_config(page_title="Explorador de Proteínas", layout="wide")

st.title("🧬 Explorador de Proteínas Interactivo")

# --- VENTANA FLOTANTE DE INSTRUCCIONES ---
@st.dialog("📖 Cómo usar esta Aplicación")
def mostrar_instrucciones():
    st.markdown("""
    ### 👋 ¡Bienvenido al Explorador Molecular!
    Esta herramienta te permite investigar la arquitectura tridimensional de proteínas esenciales y comprender sus niveles de plegamiento con ayuda de IA avanzada.
    
    ### 🎮 ¿Cómo interactuar con la proteína en 3D?
    * **Rotar:** Haz clic izquierdo dentro del recuadro de la proteína y arrastra el cursor en cualquier dirección.
    * **Zoom:** Usa la rueda de desplazamiento de tu mouse (scroll) o desliza dos dedos en el trackpad hacia arriba/abajo dentro del cuadro.
    * **Mover (Pan):** Mantén presionada la tecla `Shift` mientras haces clic izquierdo y arrastras para desplazar la molécula.
    
    ### 🧠 El Experto con IA
    Gracias a la conexión automática, Gemini ya está activo tras bambalinas. Selecciona una proteína y un nivel de plegamiento; la explicación aparecerá al instante en el panel derecho.
    """)

# --- BARRA LATERAL (CONFIGURACIÓN) ---
st.sidebar.title("Configuración")

# Botón destacado de instrucciones
if st.sidebar.button("❓ Ver Instrucciones de Uso", use_container_width=True):
    mostrar_instrucciones()

st.sidebar.markdown("---")

# CONEXIÓN AUTOMÁTICA OCULTA (Intenta leer la clave desde Secrets)
api_key_lista = False
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        st.sidebar.success("🔒 Conexión con Gemini: ACTIVA")
        api_key_lista = True
    else:
        st.sidebar.warning("⚠️ No se encontró la API Key en los Secrets del servidor.")
except Exception as e:
    st.sidebar.error(f"Error al cargar credenciales de seguridad: {e}")

st.sidebar.markdown("---")

# --- CATÁLOGO EXPANDIDO DE PROTEÍNAS (Banco de Datos PDB) ---
proteinas = {
    "Insulina (Metabolismo)": "1TRZ", 
    "Hemoglobina (Transporte de Oxígeno)": "1A3N", 
    "Colágeno (Estructura de la piel)": "1BKV",
    "Queratina (Cabello y Uñas)": "1CO4",
    "Mioglobina (Reserva de Oxígeno muscular)": "1MBN",
    "Proteína Spike (Coronavirus)": "6VXX",
    "Anticuerpo Inmunoglobulina G": "1IGY"
}

nombre_seleccionado = st.sidebar.selectbox("Proteína a estudiar:", list(proteinas.keys()))
pdb_id = proteinas[nombre_seleccionado]

# Selector de Nivel de Plegamiento
nivel = st.sidebar.radio(
    "Nivel de Plegamiento:", 
    ["Primaria (Cadena)", "Secundaria (Cintas)", "Terciaria (3D Completa)"]
)

# Definición del estilo visual para el renderizador 3Dmol
if "Primaria" in nivel:
    estilo_visual = "stick"
elif "Secundaria" in nivel:
    estilo_visual = "cartoon"
else:
    estilo_visual = "sphere"

# Subtítulo dinámico según la proteína elegida
st.subheader(f"🔍 Análisis Estructural: {nombre_seleccionado}")

# --- DISEÑO DE COLUMNAS (Visualizador vs Explicación) ---
col1, col2 = st.columns([4, 3])

with col1:
    st.markdown(f"**Representación Tridimensional: {nivel}**")
    # Código HTML insertado para conectar con la base de datos mundial PDB en vivo
    html_code = f"""
    <div style="height: 450px; width: 100%; position: relative;" 
         class='viewer_3Dmoljs' data-pdb='{pdb_id}' 
         data-backgroundcolor='0xf8f9fa' 
         data-style='{estilo_visual}:{{colorscheme:"spectrum"}}'></div>
    <script src="https://3dmol.org/build/3Dmol-min.js"></script>
    """
    components.html(html_code, height=460)

with col2:
    st.markdown("### 🧠 Explicación del Experto Bioquímico")
    
    # CONTENEDOR CON SCROLL INDEPENDIENTE (Altura fija de 430 píxeles)
    with st.container(height=430):
        if api_key_lista:
            try:
                # Conectamos con el motor de última generación Flash
                model = genai.GenerativeModel('gemini-2.5-flash')
                prompt = (
                    f"Actúa como un bioquímico experto y docente altamente didáctico. "
                    f"Explica de forma clara, amena y dinámica cómo se comporta la proteína '{nombre_seleccionado}' "
                    f"específicamente en su nivel de organización '{nivel}'. "
                    f"Detalla cómo este plegamiento específico influye directamente en su función biológica."
                )
                
                with st.spinner("Analizando enlaces moleculares con IA..."):
                    respuesta = model.generate_content(prompt)
                st.write(respuesta.text)
                
            except Exception as e:
                st.error(f"Error al procesar la consulta con Gemini: {e}")
        else:
            st.info("Para ver el análisis automático de la IA, asegúrate de configurar la clave en la pestaña 'Secrets' de tu panel de Streamlit.")
