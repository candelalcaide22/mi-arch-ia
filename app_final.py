import streamlit as st
import ezdxf
from ezdxf import recover
import io

# Configuración de página
st.set_page_config(page_title="ARCH-IA | Studio", page_icon="🏢", layout="wide")

# --- CSS AVANZADO (MANTENIENDO ESTÉTICA AL 100%) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400&display=swap');
    .stApp { background-color: #FDFCF0; }
    header[data-testid="stHeader"] { background-color: #8A9A5B !important; }
    header[data-testid="stHeader"] * { color: white !important; }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #2C2C2C !important; }
    .subtitulo-normal { font-family: 'Inter', sans-serif !important; color: #6B6B6B !important; font-size: 1rem; font-style: normal !important; }
    
    /* Color Verde Sage para el texto de las instrucciones */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, 
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] li { 
        color: #8A9A5B !important; 
        font-family: 'Inter', sans-serif !important;
    }
    
    span[data-testid="stWidgetLabel"] > div > div > p { display: none; } 
    .aria-label, [aria-hidden="true"] { display: none !important; }
    div.stButton > button { background-color: #8A9A5B !important; color: white !important; border-radius: 0px !important; border: none !important; padding: 12px !important; width: 100%; text-transform: uppercase; letter-spacing: 1.5px; }
    [data-testid="stSidebar"] { background-color: #F7F5E6 !important; }
    [data-testid="stExpander"] svg { display: none !important; }
    [data-testid="stMetricValue"] { font-family: 'Playfair Display', serif !important; color: #8A9A5B !important; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (CON INSTRUCCIÓN DE BARRA DE ALTURA) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>ARCH-IA</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.8rem; color: #8A9A5B;'>STUDIO EDITION</p>", unsafe_allow_html=True)
    st.write("---")
    
    st.write("### 📖 Protocolo de Trabajo")
    
    with st.expander("1. Preparación del Plano", expanded=True):
        st.write("""
        Para garantizar un sólido perfecto:
        * **Entidades:** Utiliza únicamente líneas (`LINE`) o polilíneas cerradas (`PLINE`).
        * **Limpieza:** Elimina bloques, sombreados o textos.
        * **Geometría:** Asegúrate de unir vértices (comando `JOIN`).
        """)
        
    with st.expander("2. Sistema de Unidades"):
        st.write("""
        Este motor trabaja con **Escala Real 1:1**:
        * **Barra de Configuración:** Utiliza el deslizador para definir la **altura deseada** (extrusión Z) de tu modelo antes de descargar.
        * Si tu proyecto está en metros, dibuja un cuadrado de 5x5 para obtener 25m².
        * El programa centrará el dibujo en el origen (0,0,0).
        """)
        
    with st.expander("3. Exportación DXF"):
        st.write("""
        **Obligatorio:**
        Al guardar en AutoCAD, selecciona:
        * **Tipo:** AutoCAD DXF.
        * **Versión:** 2010 o 2013.
        """)

    with st.expander("4. Flujo en el Modelo 3D"):
        st.write("""
        Tras la descarga:
        1. Abre el archivo en AutoCAD.
        2. Activa el estilo visual **Conceptual**.
        3. Usa `Shift` + rueda del ratón para orbitar.
        """)
    
    st.write("---")
    st.caption("Soporte: studio@arch-ia.com")

# --- CUERPO PRINCIPAL ---
st.title("The Architectural Conversion Tool")
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
st.caption("ARCH-IA Studio | v6.6")
