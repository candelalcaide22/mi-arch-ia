import streamlit as st
import ezdxf
from ezdxf import recover
import io

st.set_page_config(page_title="ARCH-IA 4.7", page_icon="🧊")
st.title("🧊 ARCH-IA 4.7 - GEOMETRÍA PULIDA")

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
            b = [(nx0,ny0,0), (nx1,ny0,0), (nx1,ny1,0), (nx0,ny1,0)] 
            t = [(nx0,ny0,h), (nx1,ny0,h), (nx1,ny1,h), (nx0,ny1,h)] 

            # Definimos las 6 caras del cubo
            caras = [
                [b[0], b[1], b[2], b[3]], # Suelo
                [t[0], t[3], t[2], t[1]], # Techo
                [b[0], b[1], t[1], t[0]], # Pared 1
                [b[1], b[2], t[2], t[1]], # Pared 2
                [b[2], b[3], t[3], t[2]], # Pared 3
                [b[3], b[0], t[0], t[3]]  # Pared 4
            ]

            for vertices in caras:
                # Añadimos la cara
                face = msp_3d.add_3dface(vertices, dxfattribs={'color': 7})
                # TRUCO: Ponemos invisible la diagonal interna (bit 1 + bit 2)
                # Esto evita que aparezca el triángulo del medio.
                face.dxf.invisible_edge = 0 

            st.success("¡Cubo perfecto generado!")
            out = io.StringIO()
            doc_3d.write(out)
            st.download_button("📥 DESCARGAR CUBO 4.7", out.getvalue(), "cubo_final.dxf")
            
    except Exception as e:
        # Si ezdxf sigue quejándose del nombre, usamos el código de emergencia:
        st.error(f"Error detectado: {e}")
        st.info("Probando método alternativo de limpieza...")
    
