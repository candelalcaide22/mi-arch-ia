import streamlit as st
import ezdxf
import io

# 1. Configuración de la interfaz
st.set_page_config(page_title="ARCH-IA 2.8", page_icon="🏗️")
st.title("🏗️ ARCH-IA 2.8 - COMPATIBILIDAD TOTAL")

# 2. Panel lateral
st.sidebar.header("Configuración")
altura_muro = st.sidebar.slider("Altura de muros (m)", 1.0, 10.0, 2.5)

# 3. Cargador de archivos
uploaded_file = st.file_uploader("Sube tu archivo .dxf", type=["dxf"])

if uploaded_file is not None:
    with st.spinner('Procesando plano...'):
        try:
            # LEER: Obtenemos los bytes y los pasamos a texto limpio
            bytes_data = uploaded_file.read()
            text_data = bytes_data.decode('latin-1', errors='ignore')
            
            # SOLUCIÓN AL ERROR 'readstr': 
            # Creamos un "archivo virtual" (StringIO) y usamos ezdxf.read()
            archivo_virtual = io.StringIO(text_data)
            doc = ezdxf.read(archivo_virtual)
            
            msp = doc.modelspace()
            
            # Crear el nuevo documento 3D
            doc_3d = ezdxf.new('R2010')
            msp_3d = doc_3d.modelspace()
            
            # Extraer líneas y polilíneas
            count = 0
            for e in msp.query('LINE LWPOLYLINE'):
                if e.dxftype() == 'LINE':
                    msp_3d.add_line(e.dxf.start, e.dxf.end, dxfattribs={'thickness': altura_muro})
                    count += 1
                elif e.dxftype() == 'LWPOLYLINE':
                    pts = e.get_points()
                    for i in range(len(pts)-1):
                        msp_3d.add_line(pts[i][:2], pts[i+1][:2], dxfattribs={'thickness': altura_muro})
                    count += 1

            if count > 0:
                # GUARDAR: Generamos el resultado
                out_buffer = io.StringIO()
                doc_3d.write(out_buffer)
                
                st.success(f"¡CONSEGUIDO! Se han convertido {count} elementos.")
                st.download_button(
                    label="📥 Descargar Modelo 3D",
                    data=out_buffer.getvalue(),
                    file_name="modelo_3d_final.dxf",
                    mime="application/dxf"
                )
            else:
                st.warning("No se detectaron líneas. Asegúrate de que el dibujo no sean bloques.")

        except Exception as e:
            st.error(f"Error técnico: {e}")

st.divider()
st.caption("ARCH-IA v2.8 | Sin usar readstr para evitar errores de versión.")
