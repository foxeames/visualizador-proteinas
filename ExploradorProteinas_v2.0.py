# Archivo: ExploradorProteinas_v2.0.py
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai

st.set_page_config(page_title="Visualizador v2.0", layout="wide")

st.title("🧬 Explorador de Proteínas v2.0")
st.write("Visualización interactiva y análisis pedagógico con IA.")

# Configurar la clave de API de Gemini de forma segura
# (En Streamlit Cloud se configura en Settings > Secrets)
api_key = st.sidebar.text_input("Introduce tu Gemini API Key:", type="password")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.sidebar.warning("Por favor, introduce tu API Key de Google AI Studio para activar la IA.")

# 1. Selector de Proteína
proteinas = {
    "Insulina": "1TRZ", 
    "Hemoglobina": "1A3N", 
    "Colágeno": "1BKV"
}
nombre = st.sidebar.selectbox("Proteína a estudiar:", list(proteinas.keys()))
pdb_id = proteinas[nombre]

# 2. Selector de Nivel de Estructura (Edutainment)
nivel = st.sidebar.radio(
    "Nivel de Plegamiento:", 
    ["Primaria (Cadena)", "Secundaria (Cintas)", "Terciaria (3D Completa)"]
)

# Definir el estilo visual según el nivel seleccionado
if "Primaria" in nivel:
    estilo_visual = "stick"  # Muestra los enlaces individuales
    descripcion_nivel = "la secuencia lineal de aminoácidos."
elif "Secundaria" in nivel:
    estilo_visual = "cartoon"  # Resalta hélices y hojas
    descripcion_nivel = "las estructuras locales como hélices alfa y hojas beta."
else:
    estilo_visual = "sphere"  # Modelo compacto molecular
    descripcion_nivel = "la estructura tridimensional global y su empaquetamiento."

st.subheader(f"🔍 Análisis: {nombre} ({nivel})")

# Columnas: Izquierda para el modelo 3D, Derecha para la IA
col1, col2 = st.columns([4, 3])

with col1:
    # Renderizador molecular interactivo usando 3Dmol.js
    html_code = f"""
    <div style="height: 450px; width: 100%; position: relative;" 
         class='viewer_3Dmoljs' data-pdb='{pdb_id}' 
         data-backgroundcolor='0xf8f9fa' 
         data-style='{estilo_visual}:{{colorscheme:"spectrum"}}'></div>
    <script src="https://3dmol.org/build/3Dmol-min.js"></script>
    """
    components.html(html_code, height=470)

with col2:
    st.markdown("### 🧠 Explicación del Experto (Gemini)")
    
    if api_key:
        with st.spinner("Consultando al experto en bioquímica..."):
            try:
                # Inicializamos el modelo (usando la generación actual)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                prompt = (
                    f"Actúa como un bioquímico experto y docente didáctico. "
                    f"Explica de forma sencilla y clara cómo se comporta la proteína '{nombre}' "
                    f"específicamente en su estructura o nivel '{nivel}'. "
                    f"Enfócate en cómo este nivel de plegamiento afecta su función biológica."
                )
                
                respuesta = model.generate_content(prompt)
                st.info(respuesta.text)
                
            except Exception as e:
                st.error(f"Hubo un problema con la consulta: {e}")
    else:
        st.info("Introduce tu API Key en la barra lateral para ver la explicación bioquímica en tiempo real.")
