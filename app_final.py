import streamlit as st
import ezdxf
from ezdxf import recover
import io

st.set_page_config(page_title="ARCH-IA 3.5", page_icon="🏗️")
st.title("🏗️ ARCH-IA 3.5 - MODO MESH")

altura_muro = st.sidebar.slider("Altura (m)", 1.0, 20.0, 5.0)
uploaded_file = st.file_uploader("Sube tu plano", type=["dxf"])

if uploaded_file is not None:
    with st.spinner('Extruyendo muros...'):
        try:
            blob = uploaded_file.read()
            doc, auditor = recover.read(io.BytesIO(blob))
            
            if not doc:
                st.error("Archivo no legible.")
                st.stop()
                
            msp = doc.modelspace()
            doc_3d = ezdxf.new('R2010')
            msp_3d = doc_3d.modelspace()
            
            def dibujar_muro_mesh(p1, p2, h):
                # Creamos los 4 puntos de la red
                # v0, v1 son la base. v2, v3 son la parte de arriba.
                vertices = [
                    (p1[0], p1[1], 0), # 0
                    (p2[0], p2[1], 0), # 1
                    (p1[0], p1[1], h), # 2
                    (p2[0], p2[1], h)  # 3
                ]
                # Creamos una malla de 2x2 (un panel sólido)
                mesh = msp_3d.add_mesh(dxfattribs={'color': 7})
                with mesh.edit_data() as data:
                    data.vertices = vertices
                    # Definimos la cara (los 4 índices de los puntos)
                    data.faces = [[0, 1, 3, 2]]

            count = 0
            for e in msp.query('LINE LWPOLYLINE POLYLINE'):
                if e.dxftype() == 'LINE':
                    dibujar_muro_mesh(e.dxf.start, e.dxf.end, altura_muro)
                    count += 1
                elif e.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                    pts = list(e.get_points())
                    for i in range(len(pts)-1):
                        dibujar_muro_mesh(pts[i], pts[i+1], altura_muro)
                        count += 1
                    if e.is_closed:
                        dibujar_muro_mesh(pts[-1], pts[0], altura_muro)
                        count += 1

            if count > 0:
                out = io.StringIO()
                doc_3d.write(out)
                st.success(f"¡MALLAS GENERADAS! {count} muros creados.")
                st.download_button("📥 Descargar Mallas 3D", out.getvalue(), "muros_mesh.dxf")
            else:
                st.warning("No se encontraron líneas.")

        except Exception as e:
            st.error(f"Error: {e}")

st.divider()
st.caption("v3.5 | Uso de Mallas (MESH) para visualización sólida garantizada.")
