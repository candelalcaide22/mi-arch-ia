import streamlit as st
import ezdxf
from ezdxf import recover
import io

st.set_page_config(page_title="ARCH-IA 3.1", page_icon="🏗️")
st.title("🏗️ ARCH-IA 3.1 - RECUPERACIÓN FORZADA")

uploaded_file = st.file_uploader("Sube tu archivo .dxf", type=["dxf"])

if uploaded_file is not None:
    with st.spinner('Forzando recuperación de datos...'):
        try:
            # LEER: Leemos el archivo tal cual viene (en binario)
            blob = uploaded_file.read()
            
            # Usamos el motor de RECUPERACIÓN de ezdxf
            # Este motor ignora errores binarios y busca el dibujo por "fuerza bruta"
            try:
                doc, auditor = recover.read(io.BytesIO(blob))
            except:
                # Si falla, probamos a decodificarlo como texto de emergencia
                text = blob.decode('latin-1', errors='ignore')
                doc = ezdxf.read(io.StringIO(text))
            
            if not doc:
                st.error("No se pudo rescatar nada. El archivo está vacío o corrupto.")
                st.stop()
                
            msp = doc.modelspace()
            doc_3d = ezdxf.new('R2010')
            msp_3d = doc_3d.modelspace()
            
            altura = st.sidebar.slider("Altura", 1.0, 10.0, 2.5)
            
            count = 0
            for e in msp.query('LINE LWPOLYLINE'):
                try:
                    if e.dxftype() == 'LINE':
                        msp_3d.add_line(e.dxf.start, e.dxf.end, dxfattribs={'thickness': altura})
                        count += 1
                    elif e.dxftype() == 'LWPOLYLINE':
                        pts = e.get_points()
                        for i in range(len(pts)-1):
                            msp_3d.add_line(pts[i][:2], pts[i+1][:2], dxfattribs={'thickness': altura})
                        count += 1
                except:
                    continue

            if count > 0:
                out = io.StringIO()
                doc_3d.write(out)
                st.success(f"¡RESUCITADO! {count} líneas recuperadas.")
                st.download_button("📥 Descargar Modelo 3D", out.getvalue(), "modelo_3d.dxf")
            else:
                st.error("Archivo leído pero no hay líneas. Dibuja algo nuevo.")

        except Exception as e:
            st.error(f"Fallo del motor: {e}")

st.divider()
st.caption("v3.1 | Motor de recuperación estructural activado.")
