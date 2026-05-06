import streamlit as st
import ezdxf
from ezdxf import recover
import io

st.set_page_config(page_title="ARCH-IA 3.3", page_icon="🏗️")
st.title("🏗️ ARCH-IA 3.3 - MUROS SÓLIDOS")

altura_muro = st.sidebar.slider("Altura de los muros (m)", 1.0, 10.0, 3.0)
uploaded_file = st.file_uploader("Sube tu plano", type=["dxf"])

if uploaded_file is not None:
    with st.spinner('Generando geometría sólida...'):
        try:
            blob = uploaded_file.read()
            doc, auditor = recover.read(io.BytesIO(blob))
            
            if not doc:
                st.error("Error al leer el archivo.")
                st.stop()
                
            msp = doc.modelspace()
            doc_3d = ezdxf.new('R2010')
            msp_3d = doc_3d.modelspace()
            
            def crear_muro_solido(p1, p2, h):
                # Creamos los 4 vértices de la cara del muro
                v1 = (p1[0], p1[1], 0)      # Base inicio
                v2 = (p2[0], p2[1], 0)      # Base fin
                v3 = (p2[0], p2[1], h)      # Tope fin
                v4 = (p1[0], p1[1], h)      # Tope inicio
                # Añadimos una 3DFACE (esto es una superficie sólida)
                msp_3d.add_3dface([v1, v2, v3, v4])

            count = 0
            for e in msp.query('LINE LWPOLYLINE POLYLINE'):
                if e.dxftype() == 'LINE':
                    crear_muro_solido(e.dxf.start, e.dxf.end, altura_muro)
                    count += 1
                
                elif e.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                    pts = list(e.get_points())
                    for i in range(len(pts)-1):
                        crear_muro_solido(pts[i], pts[i+1], altura_muro)
                        count += 1
                    if e.is_closed:
                        crear_muro_solido(pts[-1], pts[0], altura_muro)
                        count += 1

            if count > 0:
                out = io.StringIO()
                doc_3d.write(out)
                st.success(f"¡GEOMETRÍA CREADA! {count} superficies de muro generadas.")
                st.download_button("📥 Descargar Sólido 3D", out.getvalue(), "modelo_solido.dxf")
            else:
                st.warning("No se encontraron líneas.")

        except Exception as e:
            st.error(f"Error: {e}")

st.divider()
st.caption("v3.3 | Generación de 3DFaces para superficies reales.")
