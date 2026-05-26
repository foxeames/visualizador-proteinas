# Archivo definitivo: ExploradorProteinas.py
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai

# Configuración de página limpia y profesional (Estilo Joyful UI)
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
    * **Zoom:** Usa la rueda de desplazamiento de tu mouse o desliza **dos dedos hacia arriba o abajo** en el trackpad.
    * **Mover / Panear (Desplazar molécula):**
        * *Con Mouse:* Mantén presionada la tecla `Shift` mientras haces clic izquierdo y arrastras.
        * *Con Trackpad de Mac:* Mantén presionadas las teclas **`Ctrl` + `Command` (⌘)**, haz clic y arrastra.
    """)

# --- BARRA LATERAL REDISEÑADA Y COMPACTA ---
st.sidebar.title("🧪 Laboratorio Virtual")
st.sidebar.markdown("Modifica los controles para alterar el experimento en tiempo real.")

# Inyección de CSS para reducir los espacios exagerados (Padding) de la barra lateral
st.markdown(
    """
    <style>
        /* Reduce el espacio entre bloques en la barra lateral */
        [data-testid="stSidebarUserContent"] .stBlock {
            margin-bottom: -18px !important;
            padding-bottom: 0px !important;
        }
        /* Ajusta la separación general de los elementos del sidebar */
        [data-testid="stSidebar"] {
            padding-top: 1.5rem !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Botón destacado de instrucciones (Ahora más integrado)
if st.sidebar.button("❓ Guía de Uso Rápido", use_container_width=True):
    mostrar_instrucciones()

st.sidebar.markdown("---")

# CONEXIÓN AUTOMÁTICA OCULTA (Intenta leer la clave desde Secrets)
api_key_lista = False
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        st.sidebar.caption("🟢 **Gemini IA:** Conectado y Activo")
        api_key_lista = True
    else:
        st.sidebar.warning("⚠️ Falta API Key en Secrets")
except Exception as e:
    st.sidebar.error(f"Error de credenciales: {e}")

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

nombre_seleccionado = st.sidebar.selectbox("1. Selecciona una Proteína:", list(proteinas.keys()))
pdb_id = proteinas[nombre_seleccionado]

# Selector de Nivel de Plegamiento
nivel = st.sidebar.radio(
    "2. Nivel de Plegamiento:", 
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
            st.info("Para ver el análisis de la IA, asegúrate de configurar la clave en los 'Secrets' del servidor de Streamlit.")
