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

    /* Fondo y contenedores */
    .stApp {
        background-color: #FDFCF0; /* Crema discreto */
    }
    
    /* Tipografía */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #2C2C2C !important;
        font-weight: 700 !important;
    }
    
    p, span, label {
        font-family: 'Inter', sans-serif !important;
        color: #4A4A4A !important;
    }

    /* Botones y Sliders (Verde Sage) */
    div.stButton > button {
        background-color: #8A9A5B !important; /* Verde salvia */
        color: white !important;
        border-radius: 0px !important; /* Estética minimalista cuadrada */
        border: none !important;
        padding: 10px 24px !important;
        font-family: 'Inter', sans-serif !important;
        transition: 0.3s;
    }
    
    div.stButton > button:hover {
        background-color: #76844D !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    /* Sidebar con estilo limpio */
    [data-testid="stSidebar"] {
        background-color: #F7F5E6 !important;
        border-right: 1px solid #E0DDD0;
    }

    /* Input box y métricas */
    [data-testid="stMetricValue"] {
        font-family: 'Playfair Display', serif !important;
        color: #8A9A5B !important;
    }
    </style>
    """, unsafe_allow_stdio=True)

# --- SIDEBAR (INSTRUCCIONES) ---
with st.sidebar:
    st.markdown("# ARCH-IA")
    st.markdown("---")
    st.markdown("### 📖 Guía de Preparación")
    with st.expander("📝 AutoCAD Setup", expanded=False):
        st.write("Dibuja tu perímetro con LINE o PLINE.")
    with st.expander("💾 Formato de Guardado"):
        st.write("Exporta como **DXF 2010**.")
    with st.expander("🔄 Visualización"):
        st.write("Usa modo **Conceptual** y orbita.")

# --- CUERPO PRINCIPAL ---
st.title("The Architectural Conversion Tool")
st.markdown("_Elevando planos 2D a volúmenes habitables._")
st.markdown("---")

col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.subheader("Configuración")
    altura_h = st.slider("Altura de Extrusión (m)", 0.1, 50.0, 3.5)
    uploaded_file = st.file_uploader("Arrastra aquí tu plano DXF", type=["dxf"])

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

                st.subheader("Análisis de Geometría")
                m1, m2 = st.columns(2)
                m1.metric("Ancho", f"{ancho:.2f} u")
                m2.metric("Largo", f"{largo:.2f} u")

                # Generación 3D
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

                st.markdown("---")
                out = io.StringIO()
                doc_3d.write(out)
                st.download_button("📥 DESCARGAR MODELO 3D", out.getvalue(), "ARCH_IA_PRO.dxf", use_container_width=True)
                
        except Exception as e:
            st.error("Error en lectura. Verifica el formato DXF 2010.")

st.markdown("---")
st.caption("ARCH-IA Studio | v6.0 | Estética Minimalista")
