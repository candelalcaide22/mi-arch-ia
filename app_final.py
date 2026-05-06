import streamlit as st
import ezdxf
from ezdxf import recover
import io

# Configuración de página
st.set_page_config(page_title="ARCH-IA | Studio", page_icon="🏢", layout="wide")

# --- ESTILO CSS PERSONALIZADO (Look & Feel) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400&display=swap');

    /* Fondo de la aplicación */
    .stApp {
        background-color: #FDFCF0;
    }
    
    /* Tipografía para títulos */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #2C2C2C !important;
    }
    
    /* Tipografía para textos normales */
    p, span, label, .stMarkdown {
        font-family: 'Inter', sans-serif !important;
        color: #4A4A4A !important;
    }

    /* Botón personalizado Verde Sage */
    div.stButton > button {
        background-color: #8A9A5B !important;
        color: white !important;
        border-radius: 0px !important;
        border: none !important;
        padding: 12px 30px !important;
        width: 100%;
        transition: 0.3s;
        font-weight: 400;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    div.stButton > button:hover {
        background-color: #76844D !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }

    /* Estilo de la barra lateral */
    [data-testid="stSidebar"] {
        background-color: #F7F5E6 !important;
        border-right: 1px solid #E0DDD0;
    }

    /* Métricas con estilo elegante */
    [data-testid="stMetricValue"] {
        font-family: 'Playfair Display', serif !important;
        color: #8A9A5B !important;
    }
    </style>
    """, unsafe_allow_html=True) # <-- AQUÍ ESTABA EL ERROR, YA ESTÁ ARREGLADO

# --- SIDEBAR (INSTRUCCIONES) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>ARCH-IA</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📖 Guía de Preparación")
    with st.expander("📝 AutoCAD Setup", expanded=False):
        st.write("Dibuja tu perímetro con LINE o PLINE.")
    with st.expander("💾 Formato de Guardado"):
        st.write("Exporta como DXF 2010 o 2013.")
    with st.expander("🔄 Visualización"):
        st.write("Usa modo Conceptual en AutoCAD.")

# --- CUERPO PRINCIPAL ---
st.title("The Architectural Conversion Tool")
st.markdown("_Elevando planos 2D a volúmenes habitables con precisión geométrica._")
st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.subheader("Parámetros")
    altura_h = st.slider("Altura de Extrusión (m)", 0.1, 50.0, 3.5)
    uploaded_file = st.file_uploader("Cargar plano DXF", type=["dxf"])

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

                st.subheader("Análisis de Obra")
                m1, m2 = st.columns(2)
                m1.metric("Ancho total", f"{ancho:.2f} m")
                m2.metric("Largo total", f"{largo:.2f} m")

                # Generación 3D (Lógica robusta v4.9)
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

                st.markdown("<br>", unsafe_allow_html=True)
                out = io.StringIO()
                doc_3d.write(out)
                st.download_button("📥 DESCARGAR PROYECTO 3D", out.getvalue(), "ARCH_IA_MODEL.dxf", use_container_width=True)
                
        except Exception as e:
            st.error("Error de lectura: Asegúrate de usar DXF versión 2010.")

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.caption("ARCH-IA Studio | v6.1 | Design & Code")
