import streamlit as st
import ezdxf
from ezdxf import recover
import io

st.set_page_config(page_title="ARCH-IA 4.8", page_icon="🧊")
st.title("🧊 ARCH-IA 4.8 - CUBO SIN DIAGONALES")

altura_h = st.sidebar.slider("Altura (m)", 0.1, 50.0, 5.0)
uploaded_file = st.file_uploader("Sube tu cuadrado", type=["dxf"])

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
            # Centramos en el origen
            nx0, nx1, ny0, ny1 = 0, ancho, 0, largo

            doc_3d = ezdxf.new('R2010')
            msp_3d = doc_3d.modelspace()
            
            h = altura_h
            # Definimos los 8 puntos del cubo
            v = [
                (nx0, ny0, 0), (nx1, ny0, 0), (nx1, ny1, 0), (nx0, ny1, 0), # Base (0-3)
                (nx0, ny0, h), (nx1, ny0, h), (nx1, ny1, h), (nx0, ny1, h)  # Techo (4-7)
            ]

            # Creamos una Polyface Mesh (Malla polifacetada)
            # Esto evita las líneas diagonales porque AutoCAD lo ve como un solo volumen
            pface = msp_3d.add_polyface()
            pface.append_vertices(v)
            
            # Definimos las caras (conectando los índices de los puntos)
            pface.append_face([0, 1, 2, 3]) # Suelo
            pface.append_face([4, 7, 6, 5]) # Techo
            pface.append_face([0, 1, 5, 4]) # Pared frontal
            pface.append_face([1, 2, 6, 5]) # Pared derecha
            pface.append_face([2, 3, 7, 6]) # Pared trasera
            pface.append_face([3, 0, 4, 7]) # Pared izquierda

            st.success("¡Cubo sólido generado con éxito!")
            out = io.StringIO()
            doc_3d.write(out)
            st.download_button("📥 DESCARGAR CUBO 4.8", out.getvalue(), "cubo_limpio.dxf")
            
    except Exception as e:
        st.error(f"Error inesperado: {e}")
    
