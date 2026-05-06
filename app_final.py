import streamlit as st
import ezdxf
from ezdxf import recover
import io

st.set_page_config(page_title="ARCH-IA PRO", page_icon="🏢", layout="wide")

# --- MENÚ DE INSTRUCCIONES EN LA SIDEBAR ---
with st.sidebar:
    st.title("📖 Guía de Usuario")
    with st.expander("1. Preparación en AutoCAD", expanded=True):
        st.write("""
        * **Dibujo:** Usa líneas (`LINE`) o polilíneas (`PLINE`).
        * **Escala:** Dibuja en unidades reales (ej: 5x5 para 5 metros).
        * **Ubicación:** Procura dibujar cerca del origen (0,0).
        """)
    
    with st.expander("2. Formato de Guardado"):
        st.warning("⚠️ **MUY IMPORTANTE**")
        st.write("""
        El archivo debe guardarse obligatoriamente como:
        * **DXF de intercambio.**
        * Versión **AutoCAD 2010** o **2013**.
        """)
    
    with st.expander("3. Visualización 3D"):
        st.write("""
        Una vez descargues el archivo:
        1. Abre en AutoCAD.
        2. Cambia a vista **Conceptual** o **Sombreado**.
        3. Usa `Shift + Rueda` para orbitar.
        """)

# --- CUERPO PRINCIPAL ---
st.title("🏗️ ARCH-IA PRO: Conversor 2D a 3D")
st.subheader("Transforma tus planos planos en volúmenes profesionales")

col1, col2 = st.columns([1, 1])

with col1:
    altura_h = st.number_input("Altura del volumen (unidades)", min_value=0.1, max_value=100.0, value=3.0)
    uploaded_file = st.file_uploader("Sube tu archivo DXF corregido", type=["dxf"])

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

                st.success(f"✅ Archivo leído correctamente")
                st.metric("Ancho detectado", f"{ancho:.2f} m")
                st.metric("Largo detectado", f"{largo:.2f} m")

                # Generación del 3D
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

                out = io.StringIO()
                doc_3d.write(out)
                st.download_button("📥 DESCARGAR MODELO PROFESIONAL", out.getvalue(), "ARCH_IA_PRO.dxf", use_container_width=True)
                
        except Exception as e:
            st.error(f"❌ Error al procesar: Asegúrate de que el DXF sea versión 2010/2013.")
