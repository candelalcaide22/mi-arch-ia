import streamlit as st
import ezdxf
from ezdxf import recover
import io

# 1. Configuración de página
st.set_page_config(
    page_title="alcaidearchia | Studio", 
    page_icon="🏢", 
    layout="wide"
)

# --- CSS (v7.2 + Estilo de Input Numérico) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400&display=swap');
    .stApp { background-color: #FDFCF0; }
    header[data-testid="stHeader"] { background-color: #8A9A5B !important; }
    header[data-testid="stHeader"] * { color: white !important; }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #2C2C2C !important; }
    .subtitulo-normal { font-family: 'Inter', sans-serif !important; color: #6B6B6B !important; font-size: 1rem; }
    
    /* Instrucciones en Verde Sage */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, 
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] li,
    .aclaracion-verde { 
        color: #8A9A5B !important; 
        font-family: 'Inter', sans-serif !important;
        margin-bottom: 5px;
    }
    
    /* Selector de formato */
    div[data-testid="stRadio"] label p {
        font-family: sans-serif !important;
        color: #333333 !important;
        font-weight: 500 !important;
    }

    /* Estilo para el campo de entrada numérica */
    div[data-testid="stNumberInput"] {
        background-color: white;
        border-radius: 0px;
    }

    span[data-testid="stWidgetLabel"] > div > div > p { display: none; } 
    .aria-label, [aria-hidden="true"] { display: none !important; }
    div.stButton > button { background-color: #8A9A5B !important; color: white !important; border-radius: 0px !important; border: none !important; padding: 12px !important; width: 100%; text-transform: uppercase; letter-spacing: 1.5px; }
    [data-testid="stSidebar"] { background-color: #F7F5E6 !important; }
    [data-testid="stExpander"] svg { display: none !important; }
    [data-testid="stMetricValue"] { font-family: 'Playfair Display', serif !important; color: #8A9A5B !important; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>alcaidearchia</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.8rem; color: #8A9A5B;'>ESTUDIO DE ARQUITECTURA</p>", unsafe_allow_html=True)
    st.write("---")
    st.write("### 📖 Protocolo de Trabajo")
    with st.expander("1. Preparación del Plano", expanded=True):
        st.write("Líneas o polilíneas unidas (JOIN). Dibujo limpio sin bloques.")
    with st.expander("2. Sistema de Unidades"):
        st.write("Escala 1:1. **Escribe la altura exacta** en el recuadro de configuración.")
    with st.expander("3. Exportación DXF"):
        st.write("Guardar como AutoCAD DXF 2010 o 2013.")
    st.write("---")
    st.caption("alcaidearchia | Studio v7.3")

# --- CUERPO PRINCIPAL ---
st.title("La Herramienta de Conversión Arquitectónica")
st.markdown('<p class="subtitulo-normal">Geometría simplificada para proyectos de arquitectura.</p>', unsafe_allow_html=True)
st.write("<br>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.markdown("### Configuración del Proyecto")
    formato = st.radio(
        "Selecciona el formato de entrada:",
        ("AutoCAD (DXF)", "Documento (PDF)", "Nube de puntos (XYZ)", "Imagen (PNG/JPG)"),
        horizontal=True
    )
    st.write("<br>", unsafe_allow_html=True)
    st.markdown('<p class="aclaracion-verde">Indica la altura exacta (Z) para la extrusión:</p>', unsafe_allow_html=True)
    
    # CAMBIO CRÍTICO: De Slider a Number Input para precisión total
    altura_h = st.number_input(
        "Altura del Cubo (m)", 
        min_value=0.000, 
        max_value=500.000, 
        value=3.500, 
        step=0.001, 
        format="%.3f"
    )
    
    if formato == "AutoCAD (DXF)":
        uploaded_file = st.file_uploader("Subir plano DXF", type=["dxf"])
    else:
        st.info(f"Módulo para **{formato}** en desarrollo.")
        uploaded_file = None

with col2:
    if uploaded_file is not None and formato == "AutoCAD (DXF)":
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

                st.markdown("### Análisis de Medidas")
                c1, c2 = st.columns(2)
                c1.metric("Ancho", f"{ancho:.3f} m")
                c2.metric("Largo", f"{largo:.3f} m")

                doc_3d = ezdxf.new('R2010')
                msp_3d = doc_3d.modelspace()
                h = altura_h
                nx0, nx1, ny0, ny1 = 0, ancho, 0, largo
                b = [(nx0,ny0,0), (nx1,ny0,0), (nx1,ny1,0), (nx0,ny1,0)]
                t = [(nx0,ny0,h), (nx1,ny0,h), (nx1,ny1,h), (nx0,ny1,h)]
                caras = [[b[0], b[1], b[2], b[3]], [t[0], t[1], t[2], t[3]], [b[0], b[1], t[1], t[0]], [b[1], b[2], t[2], t[1]], [b[2], b[3], t[3], t[2]], [b[3], b[0], t[0], t[3]]]
                for v in caras: msp_3d.add_3dface(v)

                st.write("<br>", unsafe_allow_html=True)
                out = io.StringIO()
                doc_3d.write(out)
                st.download_button("📥 DESCARGAR PROYECTO 3D", out.getvalue(), f"ARCH_IA_{ancho:.3f}x{largo:.3f}_h{h:.3f}.dxf", use_container_width=True)
        except Exception:
            st.error("Error de lectura.")

st.write("<br><br>", unsafe_allow_html=True)
st.caption("alcaidearchia | Studio v7.3")
