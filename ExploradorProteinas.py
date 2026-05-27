# Archivo definitivo: ExploradorProteinas.py
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import json

# Configuración de página limpia y profesional (Estilo Joyful UI)
st.set_page_config(page_title="Explorador de Proteínas Pro", layout="wide")

st.title("🧬 Explorador de Proteínas Interactivo")

# --- VENTANA FLOTANTE DE INSTRUCCIONES ACTUALIZADA ---
@st.dialog("📖 Guía del Laboratorio Virtual")
def mostrar_instrucciones():
    st.markdown("""
    ### 👋 ¡Bienvenido al Explorador Molecular Avanzado!
    Esta plataforma te permite investigar cualquier proteína del catálogo mundial usando Inteligencia Artificial para traducir nombres comunes en estructuras 3D.
    
    ### 🎮 ¿Cómo interactuar con la proteína en 3D?
    * **Rotar:** Haz clic izquierdo dentro del visor y arrastra en cualquier dirección.
    * **Zoom:** Usa la rueda del mouse o desliza **dos dedos verticalmente** en el trackpad.
    * **Mover / Panear (Desplazar):** Mantén presionadas las teclas **`Ctrl` + `Command` (⌘)** en tu Mac (o `Shift` con mouse estándar), haz clic y arrastra.
    
    ### 🔍 ¿Cómo usar el Super-Buscador de la IA?
    1. Escribe el nombre común de lo que buscas (ej: *Insulina*, *Colágeno*, *Hemoglobina*) en el cuadro de la lupa.
    2. Selecciona el **origen biológico** (Humano, Cerdo, Virus, etc.) para filtrar las variantes.
    3. Haz clic en **🚀 Buscar en el Banco Mundial**. Gemini te presentará las mejores opciones reales encontradas para que elijas la exacta.
    """)

# --- BARRA LATERAL REDISEÑADA Y COMPACTA (CSS CUSTOM) ---
st.sidebar.title("🧪 Laboratorio Virtual")
st.sidebar.markdown("Controla y altera el experimento molecular en tiempo real.")

# Inyección de CSS para eliminar espacios muertos (padding) exagerados en la barra lateral
st.markdown(
    """
    <style>
        [data-testid="stSidebarUserContent"] .stBlock {
            margin-bottom: -15px !important;
            padding-bottom: 0px !important;
        }
        [data-testid="stSidebar"] {
            padding-top: 1.2rem !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Botón destacado de instrucciones
if st.sidebar.button("❓ Guía de Uso Rápido", use_container_width=True):
    mostrar_instrucciones()

st.sidebar.markdown("---")

# CONEXIÓN AUTOMÁTICA OCULTA (Secrets)
api_key_lista = False
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        api_key_lista = True
except:
    pass

# --- ARQUITECTURA DEL FILTRO CRUZADO ---
st.sidebar.markdown("### 🔍 Buscador Molecular Avanzado")

nombre_buscado = st.sidebar.text_input("Escribe el nombre de la proteína:", value="Hemoglobina", placeholder="Ej: Insulina, Colágeno, Spike...")

organismo = st.sidebar.selectbox(
    "Origen biológico (Especie):",
    ["Humano", "Cerdo (Porcino)", "Ratón (Roedor)", "Res (Bovino)", "Bacteria", "Virus", "Todos"]
)

# Inicializamos estados en la memoria de Streamlit para controlar el flujo de búsqueda
if "opciones_pdb" not in st.session_state:
    st.session_state.opciones_pdb = {"Hemoglobina Humana Estándar": "1A3N"}
if "nombre_seleccionado" not in st.session_state:
    st.session_state.nombre_seleccionado = "Hemoglobina Humana Estándar"
if "pdb_id" not in st.session_state:
    st.session_state.pdb_id = "1A3N"

# Botón disparador para ejecutar la búsqueda (Protege el consumo desmedido de tokens)
if st.sidebar.button("🚀 Buscar en el Banco Mundial", use_container_width=True):
    if api_key_lista and nombre_buscado.strip():
        try:
            with st.spinner("Gemini indexando el banco PDB..."):
                model = genai.GenerativeModel(
                    'gemini-2.5-flash',
                    generation_config={"response_mime_type": "application/json"}
                )
                
                prompt_busqueda = (
                    f"Actúa como un indexador bioinformático estricto del Protein Data Bank (PDB). "
                    f"El usuario busca la proteína '{nombre_buscado}' originaria de '{organismo}'. "
                    f"Genera una lista de hasta 3 opciones válidas de códigos PDB reales de 4 caracteres. "
                    f"Devuelve un objeto JSON donde las llaves sean el 'Nombre Descriptivo (Especie)' y los valores sean el 'CODIGO' de 4 caracteres. "
                    f"Ejemplo: {{\"Insulina Humana Activa\": \"1TRZ\"}}"
                )
                
                respuesta_raw = model.generate_content(prompt_busqueda).text
                diccionario_detectado = json.loads(respuesta_raw.strip())
                
                if diccionario_detectado:
                    st.session_state.opciones_pdb = diccionario_detectado
                    st.session_state.nombre_seleccionado = list(diccionario_detectado.keys())[0]
                    st.session_state.pdb_id = list(diccionario_detectado.values())[0]
                    st.sidebar.success("¡Coincidencias encontradas!")
                    st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error de formato o respuesta: {e}")
    else:
        st.sidebar.warning("La IA de búsqueda requiere credenciales activas.")

st.sidebar.markdown("---")

# Despliegue de resultados dinámicos entregados por la IA
if st.session_state.opciones_pdb:
    def actualizar_seleccion():
        seleccion = st.session_state.selector_dinamico
        st.session_state.pdb_id = st.session_state.opciones_pdb[seleccion]
        st.session_state.nombre_seleccionado = seleccion

    indice_actual = list(st.session_state.opciones_pdb.keys()).index(st.session_state.nombre_seleccionado) if st.session_state.nombre_seleccionado in st.session_state.opciones_pdb else 0

    opcion_elegida = st.sidebar.selectbox(
        "🎯 Coincidencias encontradas (Elige una):", 
        list(st.session_state.opciones_pdb.keys()),
        index=indice_actual,
        key="selector_dinamico",
        on_change=actualizar_seleccion
    )

# Selector de Nivel de Plegamiento
nivel = st.sidebar.radio(
    "🎛️ Nivel de Plegamiento:", 
    ["Primaria (Cadena)", "Secundaria (Cintas)", "Terciaria (3D Completa)"]
)

# Definición del estilo visual 3D
if "Primaria" in nivel:
    estilo_visual = "stick"
elif "Secundaria" in nivel:
    estilo_visual = "cartoon"
else:
    estilo_visual = "sphere"

# Subtítulo dinámico de la pantalla principal
st.subheader(f"🔍 Análisis Estructural en Vivo: {st.session_state.nombre_seleccionado} ({st.session_state.pdb_id})")

# --- DISEÑO DE COLUMNAS (Visualizador 3D vs Explicación) ---
col1, col2 = st.columns([4, 3])

with col1:
    st.markdown(f"**Representación Tridimensional: {nivel}**")
    
    # Inyección del componente 3Dmol.js mapeando la variable reactiva pdb_id
    html_code = f"""
    <div style="height: 450px; width: 100%; position: relative;" 
         class='viewer_3Dmoljs' data-pdb='{st.session_state.pdb_id}' 
         data-backgroundcolor='0xf8f9fa' 
         data-style='{estilo_visual}:{{colorscheme:"spectrum"}}'></div>
    <script src="https://3dmol.org/build/3Dmol-min.js"></script>
    """
    components.html(html_code, height=460)

with col2:
    st.markdown("### 🧠 Explicación del Experto Bioquímico")
    
    with st.container(height=430):
        if api_key_lista:
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                prompt_explicacion = (
                    f"Actúa como un bioquímico experto y docente didáctico. "
                    f"Explica de forma clara y amena cómo se comporta la estructura con código PDB '{st.session_state.pdb_id}' "
                    f"en su nivel de organización '{nivel}'. Detalla de qué manera influye este plegamiento en su función biológica."
                )
                with st.spinner("Consultando al experto..."):
                    respuesta = model.generate_content(prompt_explicacion)
                st.write(respuesta.text)
            except:
                st.info("🧬 El visualizador 3D está operando de forma autónoma conectado al banco mundial PDB. El análisis avanzado de Gemini se encuentra temporalmente en pausa por cuota del servidor.")
        else:
            st.info("🧬 El visualizador 3D está activo. Conecta la API Key en los Secrets para habilitar las explicaciones automáticas de la IA.")
