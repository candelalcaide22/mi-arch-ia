import streamlit as st
import ezdxf
from ezdxf import recover
import io

st.set_page_config(page_title="ARCH-IA 4.4", page_icon="🧊")
st.title("🧊 ARCH-IA 4.4 - UNIDADES REALES")

st.info("💡 Consejo: Si dibujas un cuadrado de 10x10 en AutoCAD, pon '10' en el slider para un cubo perfecto.")

# Slider de altura
altura_deseada = st.sidebar.number_input("Altura en unidades (m)", min_value=0.1, max_value=1000.0, value=5.0)

uploaded_file = st.file_uploader("Sube tu dibujo a escala real", type=["dxf"])

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
            
            ancho = x1 - x0
            largo = y1 - y0
            st.write(f"📏 Medidas detectadas en AutoCAD: **{ancho:.2f} x {largo:.2f}** unidades.")

            doc_3d = ezdxf.new('R2010')
            msp_3d = doc_3d.modelspace()
            
            h = altura_deseada
            # Vértices (Base Z=0, Techo Z=h)
            b = [(x0,y0,0), (x1,y0,0), (x1,y1,0), (x0,y1,0)]
            t = [(x0,y0,h), (x1,y0,h), (x1,y1,h), (x0,y1,h)]

            # Crear el sólido (6 caras)
            caras = [
                [b[0], b[1], b[2], b[3]], # Suelo
                [t[0], t[1], t[2], t[3]], # Techo
                [b[0], b[1], t[1], t[2]], # Pared 1
                [b[1], b[2], t[2], t[3]], # Pared 2
                [b[2], b[3], t[3], t[0]], # Pared 3
                [b[3], b[0], t[0], t[1]]  # Pared 4
            ]
            
            for vertices in caras:
                msp_3d.add_3dface(vertices, dxfattribs={'color': 7})

            st.success(f"¡Cubo de {h} unidades de alto creado!")
            out = io.StringIO()
            doc_3d.write(out)
            st.download_button("📥 DESCARGAR 3D REAL", out.getvalue(), "modelo_escala_real.dxf")
            
    except Exception as e:
        st.error(f"Error técnico: {e}")
    
