# Archivo: ExploradorProteinas_v1.0.py
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Visualizador de Proteínas", layout="wide")

st.title("🧬 Explorador de Proteínas - v1.0")
st.write("Herramienta pedagógica para entender el plegamiento proteico.")

# Diccionario de nombres humanos a códigos PDB
proteinas = {
    "Insulina": "1TRZ",
    "Hemoglobina": "1A3N",
    "Colágeno": "1BKV"
}

# Selector amigable
nombre_seleccionado = st.selectbox("Elige la proteína que quieres estudiar:", list(proteinas.keys()))
pdb_id = proteinas[nombre_seleccionado]

st.write(f"Visualizando: **{nombre_seleccionado}** (Código PDB: {pdb_id})")

# HTML/JS para cargar 3Dmol.js (El estándar para visualización molecular)
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://3dmol.org/build/3Dmol-min.js"></script>
</head>
<body>
    <div style="height: 500px; width: 100%; position: relative;" 
         class='viewer_3Dmoljs' 
         data-pdb='{pdb_id}' 
         data-backgroundcolor='0xffffff' 
         data-style='cartoon:{{colorscheme:"spectrum"}}'>
    </div>
</body>
</html>
"""

components.html(html_code, height=550)

st.info("💡 Tip: Puedes rotar la molécula con el clic izquierdo y hacer zoom con la rueda del ratón.")