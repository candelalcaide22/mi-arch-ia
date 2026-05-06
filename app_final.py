import streamlit as st
import ezdxf
from ezdxf import recover
import io

# Configuración de página
st.set_page_config(page_title="ARCH-IA | Studio", page_icon="🏢", layout="wide")

# --- CSS AVANZADO: LIMPIEZA PROFUNDA ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400&display=swap');

    /* 1. Fondo y Base */
    .stApp { background-color: #FDFCF0; }
    
    /* 2. Barra superior (Header) en Verde Sage */
    header[data-testid="stHeader"] {
        background-color: #8A9A5B !important;
    }
    header[data-testid="stHeader"] * {
        color: white !important;
    }

    /* 3. Tipografías */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #2C2C2C !important;
    }
    .subtitulo-normal {
        font-family: 'Inter', sans-serif !important;
        color: #6B6B6B !important;
        font-size: 1rem;
        font-style: normal !important; /* Quita la cursiva */
    }

    /* 4. Limpieza de elementos "fantasmas" a la izquierda */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #4A4A4A !important;
    }
    /* Oculta textos de accesibilidad que se pisan */
    span[data-testid="stWidgetLabel"] > div > div > p { display: none; } 
    .aria-label, [aria-hidden="true"] { display: none !important; }

    /* 5. Botón Sage */
    div.stButton > button {
        background-color: #8A9A5B !important;
        color: white !important;
        border-radius: 0px !important;
        border: none !important;
        padding: 12px !important;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }

    /* 6. Barra lateral limpia */
    [data-testid="stSidebar"] {
        background-color: #F7F5E6 !important;
    }
    /* Quitar iconos de expanders para evitar que se pisen */
    [data-testid="stExpander"] svg { display: none !important; }

    /* 7. Métricas */
    [data-testid="stMetricValue"] {
        font-family: 'Playfair Display', serif !important;
        color: #8A9A5B !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>ARCH-IA</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.8rem;'>STUDIO EDITION</p>", unsafe_allow_html=True)
    st.write("---")
    st.write("### Instrucciones")
    with st.expander("Formato"):
        st.write("DXF 2010 / 2013")
    with st.expander("Escala"):
        st.write("Unidades reales (1=1m)")
    with st.expander("Visualización"):
        st.write("Modo Conceptual")

# --- CUERPO PRINCIPAL ---
st.title("The Architectural Conversion Tool")
# El subtítulo ahora es letra normal (clase subtitulo-normal)
st.markdown('<p class="subtitulo-normal">Geometría simplificada para proyectos de arquitectura.</p>', unsafe_allow_html=True)
st.write("<br>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.markdown("### Configuración")
    altura_h = st.slider("Altura de Extrusión", 0.1, 50.0, 3.5)
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

                st.write("<br>", unsafe_allow_html=True)
                out = io.StringIO()
                doc_3d.write(out)
                st.download_button("📥 DESCARGAR PROYECTO 3D", out.getvalue(), "ARCH_IA_PRO.dxf", use_container_width=True)
                
        except Exception:
            st.error("Error de lectura.")

st.write("<br><br>", unsafe_allow_html=True)
st.caption("ARCH-IA Studio | v6.3")
