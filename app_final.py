import streamlit as st
import ezdxf
from ezdxf import recover
import io

# Configuración de página
st.set_page_config(page_title="ARCH-IA | Studio", page_icon="🏢", layout="wide")

# --- ESTILO CSS REVISADO (Sin errores de superposición) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400&display=swap');

    /* Fondo general */
    .stApp {
        background-color: #FDFCF0;
    }
    
    /* Títulos con Playfair Display */
    h1, h2, h3, [data-testid="stHeader"] {
        font-family: 'Playfair Display', serif !important;
        color: #2C2C2C !important;
    }
    
    /* Texto general e Interfaz */
    .stMarkdown, p, label {
        font-family: 'Inter', sans-serif !important;
        color: #4A4A4A !important;
    }

    /* Ajuste específico para evitar que las letras se pisen en la Sidebar */
    [data-testid="stSidebar"] * {
        font-family: 'Inter', sans-serif !important;
    }

    /* Botón Sage personalizado - Limpio */
    div.stButton > button {
        background-color: #8A9A5B !important;
        color: white !important;
        border-radius: 2px !important;
        border: none !important;
        padding: 0.6rem 1rem !important;
        width: 100%;
        font-family: 'Inter', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    div.stButton > button:hover {
        background-color: #76844D !important;
    }

    /* Barra lateral */
    [data-testid="stSidebar"] {
        background-color: #F7F5E6 !important;
    }

    /* Métricas */
    [data-testid="stMetricValue"] {
        font-family: 'Playfair Display', serif !important;
        color: #8A9A5B !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #2C2C2C;'>ARCH-IA</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.write("### 📖 Guía Rápida")
    with st.expander("📝 Formato", expanded=False):
        st.write("Usa DXF versión 2010 o 2013.")
    with st.expander("📐 Escala"):
        st.write("Dibuja en unidades reales en AutoCAD.")
    with st.expander("🧱 3D"):
        st.write("Visualiza en modo Conceptual.")

# --- CUERPO PRINCIPAL ---
st.title("The Architectural Conversion Tool")
st.markdown("_Geometría simplificada para proyectos de arquitectura._")
st.write("") # Espaciador

col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.markdown("### Configuración")
    altura_h = st.slider("Altura de Extrusión (unidades)", 0.1, 50.0, 3.5)
    uploaded_file = st.file_uploader("Subir plano DXF", type=["dxf"])

with col2:
    if uploaded_file is not None:
        try:
            blob = uploaded_file.read()
            doc, auditor = recover.read(io.BytesIO(blob))
            msp = doc.modelspace()
            
            puntos = []
            for e in msp.query('LINE LWPOLYLINE'):
                if e.dxftype() == 'LINE': puntos.extend([e.dxf.start, e.dxf.end])
                else: puntos.extend(e.get_points())
            
            if puntos:
                xs, ys = [p[0] for p in puntos], [p[1] for p in puntos]
                x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
                ancho, largo = x1 - x0, y1 - y0

                st.markdown("### Análisis")
                c1, c2 = st.columns(2)
                c1.metric("Ancho", f"{ancho:.2f}")
                c2.metric("Largo", f"{largo:.2f}")

                # Lógica de construcción del cubo
                doc_3d = ezdxf.new('R2010')
                msp_3d = doc_3d.modelspace()
                h = altura_h
                nx0, nx1, ny0, ny1 = 0, ancho, 0, largo
                
                b = [(nx0,ny0,0), (nx1,ny0,0), (nx1,ny1,0), (nx0,ny1,0)]
                t = [(nx0,ny0,h), (nx1,ny0,h), (nx1,ny1,h), (nx0,ny1,h)]

                caras = [
                    [b[0], b[1], b[2], b[3]], [t[0], t[1], t[2], t[3]],
                    [b[0], b[1], t[1], t[0]], [b[1], b[2], t[2], t[1]],
                    [b[2], b[3], t[3], t[2]], [b[3], b[0], t[0], t[3]]
                ]
                for v in caras: msp_3d.add_3dface(v)

                st.write("")
                out = io.StringIO()
                doc_3d.write(out)
                st.download_button("📥 DESCARGAR PROYECTO 3D", out.getvalue(), "ARCH_IA_MODEL.dxf", use_container_width=True)
                
        except Exception:
            st.error("Error al leer el archivo. Revisa el formato.")

st.write("---")
st.caption("ARCH-IA Studio | v6.2")
