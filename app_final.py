import streamlit as st
import ezdxf
from ezdxf import recover
import io

st.set_page_config(page_title="ARCH-IA 3.7", page_icon="🏗️")
st.title("🏗️ ARCH-IA 3.7 - CONVERSIÓN A SÓLIDO")

altura = st.sidebar.slider("Altura del cubo/muro (m)", 1.0, 20.0, 5.0)

uploaded_file = st.file_uploader("Sube tu cuadrado 2D", type=["dxf"])

if uploaded_file is not None:
    with st.spinner('Extruyendo geometría...'):
        try:
            blob = uploaded_file.read()
            doc, auditor = recover.read(io.BytesIO(blob))
            msp = doc.modelspace()
            
            doc_3d = ezdxf.new('R2010')
            msp_3d = doc_3d.modelspace()
            
            def dibujar_prisma_completo(p1, p2, h):
                # Coordenadas de los 8 vértices de un tramo sólido
                # (Asumiendo un grosor mínimo para que AutoCAD lo vea como objeto)
                v0 = (p1[0], p1[1], 0)  # Base A
                v1 = (p2[0], p2[1], 0)  # Base B
                v2 = (p1[0], p1[1], h)  # Techo A
                v3 = (p2[0], p2[1], h)  # Techo B
                
                # PAREDES LATERALES (3DFACES)
                # Cara frontal
                msp_3d.add_3dface([v0, v1, v3, v2], dxfattribs={'color': 7})
                
                # ESTRUCTURA DE ALAMBRE (Para asegurar que se vea en cualquier modo)
                msp_3d.add_line(v0, v1, dxfattribs={'color': 7}) # Línea suelo
                msp_3d.add_line(v2, v3, dxfattribs={'color': 7}) # Línea techo
                msp_3d.add_line(v0, v2, dxfattribs={'color': 7}) # Pilar 1
                msp_3d.add_line(v1, v3, dxfattribs={'color': 7}) # Pilar 2

            count = 0
            # Procesamos el cuadrado (ya sea por líneas sueltas o polilínea)
            for e in msp.query('LINE LWPOLYLINE POLYLINE'):
                if e.dxftype() == 'LINE':
                    dibujar_prisma_completo(e.dxf.start, e.dxf.end, altura)
                    count += 1
                elif e.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                    pts = list(e.get_points())
                    for i in range(len(pts)-1):
                        dibujar_prisma_completo(pts[i], pts[i+1], altura)
                        count += 1
                    if e.is_closed:
                        dibujar_prisma_completo(pts[-1], pts[0], altura)
                        count += 1

            if count > 0:
                out = io.StringIO()
                doc_3d.write(out)
                st.success(f"¡CUBO GENERADO! {count} caras creadas.")
                st.download_button("📥 Descargar Modelo 3D", out.getvalue(), "cubo_3d.dxf")

        except Exception as e:
            st.error(f"Error: {e}")

st.divider()
st.caption("v3.7 | Conversión directa de vectores 2D a caras 3D cerradas.")
