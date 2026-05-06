import streamlit as st
import ezdxf
from ezdxf import recover
import io

st.set_page_config(page_title="ARCH-IA 4.9", page_icon="🧊")
st.title("🧊 ARCH-IA 4.9 - SOLUCIÓN DEFINITIVA")

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
            nx0, nx1, ny0, ny1 = 0, ancho, 0, largo

            doc_3d = ezdxf.new('R2010')
            msp_3d = doc_3d.modelspace()
            
            h = altura_h
            # Definimos los 8 vértices
            b0, b1, b2, b3 = (nx0, ny0, 0), (nx1, ny0, 0), (nx1, ny1, 0), (nx0, ny1, 0)
            t0, t1, t2, t3 = (nx0, ny0, h), (nx1, ny0, h), (nx1, ny1, h), (nx0, ny1, h)

            # Dibujamos las 6 caras como 3DFACES independientes
            # Usamos el formato más básico posible para evitar errores de len()
            msp_3d.add_3dface([b0, b1, b2, b3]) # Suelo
            msp_3d.add_3dface([t0, t1, t2, t3]) # Techo
            msp_3d.add_3dface([b0, b1, t1, t0]) # Frontal
            msp_3d.add_3dface([b1, b2, t2, t1]) # Derecha
            msp_3d.add_3dface([b2, b3, t3, t2]) # Trasera
            msp_3d.add_3dface([b3, b0, t0, t3]) # Izquierda

            st.success("¡CUBO GENERADO!")
            out = io.StringIO()
            doc_3d.write(out)
            st.download_button("📥 DESCARGAR CUBO 4.9", out.getvalue(), "cubo_arquitectura.dxf")
            
    except Exception as e:
        st.error(f"Error: {e}")
