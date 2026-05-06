import streamlit as st
import ezdxf
from ezdxf import recover
import io

st.set_page_config(page_title="ARCH-IA 4.0", page_icon="🧊")
st.title("🧊 ARCH-IA 4.0 - GENERADOR DE CUBOS")

# Queremos que el usuario elija la altura
altura = st.sidebar.slider("Altura del cubo (m)", 1.0, 20.0, 5.0)

uploaded_file = st.file_uploader("Sube tu cuadrado 2D", type=["dxf"])

if uploaded_file is not None:
    with st.spinner('Construyendo sólido...'):
        try:
            blob = uploaded_file.read()
            doc, auditor = recover.read(io.BytesIO(blob))
            msp = doc.modelspace()
            
            # Nuevo archivo 3D
            doc_3d = ezdxf.new('R2010')
            msp_3d = doc_3d.modelspace()
            
            # 1. Encontrar los límites de tu cuadrado (Min y Max)
            todos_los_puntos = []
            for e in msp.query('LINE LWPOLYLINE'):
                if e.dxftype() == 'LINE':
                    todos_los_puntos.extend([e.dxf.start, e.dxf.end])
                else:
                    todos_los_puntos.extend(e.get_points())
            
            if todos_los_puntos:
                xs = [p[0] for p in todos_los_puntos]
                ys = [p[1] for p in todos_los_puntos]
                xmin, xmax = min(xs), max(xs)
                ymin, ymax = min(ys), max(ys)

                # 2. Definir los 8 vértices del cubo
                # Base (Z=0)
                v0 = (xmin, ymin, 0)
                v1 = (xmax, ymin, 0)
                v2 = (xmax, ymax, 0)
                v3 = (xmin, ymax, 0)
                # Techo (Z=altura)
                v4 = (xmin, ymin, altura)
                v5 = (xmax, ymin, altura)
                v6 = (xmax, ymax, altura)
                v7 = (xmin, ymax, altura)

                # 3. Crear las 6 caras del cubo (esto lo hace sólido)
                # Paredes laterales
                msp_3d.add_3dface([v0, v1, v5, v4]) # Frontal
                msp_3d.add_3dface([v1, v2, v6, v5]) # Derecha
                msp_3d.add_3dface([v2, v3, v7, v6]) # Trasera
                msp_3d.add_3dface([v3, v0, v4, v7]) # Izquierda
                # Tapas
                msp_3d.add_3dface([v0, v1, v2, v3]) # Suelo
                msp_3d.add_3dface([v4, v5, v6, v7]) # Techo

                st.success("¡CUBO 3D CREADO!")
                
                out = io.StringIO()
                doc_3d.write(out)
                st.download_button("📥 DESCARGAR CUBO", out.getvalue(), "cubo_3d.dxf")
            else:
                st.error("No detecto el cuadrado en tu archivo.")

        except Exception as e:
            st.error(f"Error: {e}")

st.divider()
st.caption("v4.0 | Generación de prisma rectangular cerrado.")
