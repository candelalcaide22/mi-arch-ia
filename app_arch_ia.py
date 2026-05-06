import streamlit as st
import ezdxf
import io

# 1. Configuración de la interfaz
st.set_page_config(page_title="ARCH-IA 2.7", page_icon="🏗️")
st.title("🏗️ ARCH-IA 2.7 - CONEXIÓN DIRECTA")

# 2. Panel lateral
st.sidebar.header("Configuración")
altura_muro = st.sidebar.slider("Altura de muros (m)", 1.0, 10.0, 2.5)

# 3. Cargador de archivos (Simplificado al máximo)
uploaded_file = st.file_uploader("Sube tu archivo .dxf", type=["dxf"])

if uploaded_file is not None:
    with st.spinner('Procesando...'):
        try:
            # LEER: Convertimos el archivo subido a una cadena de texto directamente
            # Esto evita que la librería se confunda con los "bytes"
            bytes_data = uploaded_file.read()
            text_data = bytes_data.decode('latin-1', errors='ignore')
            
            # Cargamos el documento desde el texto puro
            doc = ezdxf.readstr(text_data)
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
                # GUARDAR: De la forma más compatible para Streamlit
                out_buffer = io.StringIO()
                doc_3d.write(out_buffer)
                
                st.success(f"¡ÉXITO! Se han convertido {count} elementos.")
                st.download_button(
                    label="📥 Descargar Modelo 3D",
                    data=out_buffer.getvalue(), # Enviamos el texto directo
                    file_name="modelo_3d_arch_ia.dxf",
                    mime="text/plain" # Usamos texto plano para evitar errores de descarga
                )
            else:
                st.warning("El archivo se leyó bien, pero no encontré líneas. ¿Están en la capa '0'?")

        except Exception as e:
            st.error(f"Error crítico: {e}")
            st.info("Si ves 'readstr', es que la versión de la librería es muy antigua. Avisame.")

st.divider()
st.caption("ARCH-IA v2.7 | Modo de lectura de texto directo.")
