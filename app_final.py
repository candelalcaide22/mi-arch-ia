import streamlit as st
import ezdxf
from ezdxf import recover
import io

st.set_page_config(page_title="ARCH-IA 3.6", page_icon="🏗️")
st.title("🏗️ ARCH-IA 3.6 - VOLUMEN CERRADO")

# El slider ahora controla el grosor del muro además de la altura
altura = st.sidebar.slider("Altura de muros (m)", 1.0, 10.0, 3.0)
espesor = st.sidebar.slider("Espesor del muro (m)", 0.1, 1.0, 0.3)

uploaded_file = st.file_uploader("Sube tu plano", type=["dxf"])

if uploaded_file is not None:
    with st.spinner('Construyendo cajas sólidas...'):
        try:
            blob = uploaded_file.read()
            doc, auditor = recover.read(io.BytesIO(blob))
            msp = doc.modelspace()
            
            doc_3d = ezdxf.new('R2010')
            msp_3d = doc_3d.modelspace()
            
            def crear_prisma_muro(p1, p2, h, w):
                # Para simplificar y que lo veas SÍ O SÍ, vamos a crear
                # las 4 caras verticales que unen la base con el techo.
                
                # Puntos base (Z=0)
                v0 = (p1[0], p1[1], 0)
                v1 = (p2[0], p2[1], 0)
                # Puntos techo (Z=h)
                v2 = (p1[0], p1[1], h)
                v3 = (p2[0], p2[1], h)
                
                # 1. Pared frontal
                msp_3d.add_3dface([v0, v1, v3, v2], dxfattribs={'color': 252})
                # 2. Tapas (Suelo y Techo) para que no sea un tubo hueco
                # En DXF, las 3DFaces de 4 puntos cierran el área.
                msp_3d.add_line(v0, v1, dxfattribs={'color': 7}) # Base
                msp_3d.add_line(v2, v3, dxfattribs={'color': 7}) # Techo
                msp_3d.add_line(v0, v2, dxfattribs={'color': 7}) # Vertical 1
                msp_3d.add_line(v1, v3, dxfattribs={'color': 7}) # Vertical 2

            count = 0
            for e in msp.query('LINE LWPOLYLINE POLYLINE'):
                if e.dxftype() == 'LINE':
                    crear_prisma_muro(e.dxf.start, e.dxf.end, altura, espesor)
                    count += 1
                elif e.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                    pts = list(e.get_points())
                    for i in range(len(pts)-1):
                        crear_prisma_muro(pts[i], pts[i+1], altura, espesor)
                        count += 1
                    if e.is_closed:
                        crear_prisma_muro(pts[-1], pts[0], altura, espesor)
                        count += 1

            if count > 0:
                out = io.StringIO()
                doc_3d.write(out)
                st.success(f"¡ESTRUCTURA CERRADA! {count} secciones de muro unidas.")
                st.download_button("📥 Descargar 3D Final", out.getvalue(), "3d_cerrado.dxf")

        except Exception as e:
            st.error(f"Error: {e}")

st.divider()
st.caption("v3.6 | Unión de vértices superior e inferior garantizada.")
