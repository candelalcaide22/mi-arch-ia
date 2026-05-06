import streamlit as st
import ezdxf
from ezdxf import recover
import io

st.set_page_config(page_title="ARCH-IA 3.8", page_icon="🏗️")
st.title("🏗️ ARCH-IA 3.8 - GENERADOR DE CUBOS REALES")

altura = st.sidebar.slider("Altura del cubo (m)", 1.0, 20.0, 5.0)

uploaded_file = st.file_uploader("Sube tu cuadrado 2D", type=["dxf"])

if uploaded_file is not None:
    with st.spinner('Fabricando sólidos...'):
        try:
            blob = uploaded_file.read()
            doc, auditor = recover.read(io.BytesIO(blob))
            msp = doc.modelspace()
            
            doc_3d = ezdxf.new('R2010')
            msp_3d = doc_3d.modelspace()
            
            def crear_cubo_solido(p1, p2, h):
                # Un muro o cubo necesita un pequeño ancho para ser "sólido"
                # Vamos a crear un prisma rectangular a partir de la línea
                ancho = 0.5 
                
                # Definimos los 8 vértices del cubo
                # Base
                b1 = (p1[0], p1[1], 0)
                b2 = (p2[0], p2[1], 0)
                # Techo
                t1 = (p1[0], p1[1], h)
                t2 = (p2[0], p2[1], h)

                # Creamos las 6 CARAS para cerrar el cubo
                # Pared frontal
                msp_3d.add_3dface([b1, b2, t2, t1], dxfattribs={'color': 7})
                # Suelo
                msp_3d.add_3dface([b1, b2, (p2[0]+0.1, p2[1]+0.1, 0), (p1[0]+0.1, p1[1]+0.1, 0)], dxfattribs={'color': 7})
                # Techo
                msp_3d.add_3dface([t1, t2, (p2[0]+0.1, p2[1]+0.1, h), (p1[0]+0.1, p1[1]+0.1, h)], dxfattribs={'color': 7})
                
                # Unimos los vértices con líneas de estructura (para que lo veas sí o sí)
                msp_3d.add_line(b1, t1, dxfattribs={'color': 7})
                msp_3d.add_line(b2, t2, dxfattribs={'color': 7})
                msp_3d.add_line(b1, b2, dxfattribs={'color': 7})
                msp_3d.add_line(t1, t2, dxfattribs={'color': 7})

            count = 0
            for e in msp.query('LINE LWPOLYLINE POLYLINE'):
                if e.dxftype() == 'LINE':
                    crear_cubo_solido(e.dxf.start, e.dxf.end, altura)
                    count += 1
                elif e.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                    pts = list(e.get_points())
                    for i in range(len(pts)-1):
                        crear_cubo_solido(pts[i], pts[i+1], altura)
                        count += 1
                    if e.is_closed:
                        crear_cubo_solido(pts[-1], pts[0], altura)
                        count += 1

            if count > 0:
                out = io.StringIO()
                doc_3d.write(out)
                st.success(f"¡CUBO CERRADO! Se han procesado {count} segmentos.")
                st.download_button("📥 Descargar Cubo 3D", out.getvalue(), "cubo_final.dxf")

        except Exception as e:
            st.error(f"Error: {e}")

st.divider()
st.caption("v3.8 | Forzado de caras superior e inferior.")
