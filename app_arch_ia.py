import streamlit as st
import ezdxf
import io

# 1. Configuración de la interfaz
st.set_page_config(page_title="ARCH-IA 2.5", page_icon="🏗️")
st.title("🏗️ ARCH-IA 2.5 - EXTRACCIÓN BINARIA")
st.subheader("Conversor Inteligente de Planos a 3D")

# 2. Panel lateral
st.sidebar.header("Configuración")
altura_muro = st.sidebar.slider("Altura del muro (m)", 1.0, 10.0, 2.5)

# 3. Interfaz de carga
uploaded_file = st.file_uploader("Sube tu archivo .dxf", type=["dxf"])

def motor_extraccion_binaria(file):
    # Leemos el archivo completo como bytes (crudo)
    blob = file.read()
    
    # INTENTO 1: El método más directo para archivos binarios/híbridos
    try:
        # ezdxf.read() puede aceptar un chorro de bytes directamente si usamos BytesIO
        return ezdxf.read(io.BytesIO(blob))
    except Exception as e:
        st.warning(f"Intento binario fallido: {e}. Probando bypass de texto...")
    
    # INTENTO 2: Forzar la limpieza de carácteres nulos que rompen la lectura
    try:
        # El error 11810 suele ser por carácteres nulos o binarios incrustados.
        # Vamos a decodificar y QUITAR todo lo que no sea ASCII antes de que la librería lo vea.
        text_data = blob.decode('latin-1', errors='ignore')
        # Filtramos: solo nos quedamos con carácteres que AutoCAD entiende en un DXF de texto
        filtered_text = "".join(c for c in text_data if ord(c) < 128 or c in '\n\r\t')
        return ezdxf.readstr(filtered_text)
    except Exception as e:
        st.error(f"Fallo estructural: {e}")
        return None

# 4. Lógica de ejecución
if uploaded_file is not None:
    with st.spinner('Forzando la lectura de los datos...'):
        try:
            doc = motor_extraccion_binaria(uploaded_file)
            
            if doc is None:
                st.error("🚨 El archivo es ilegible para esta versión de la librería.")
                st.info("ÚLTIMA ESPERANZA: Copia tu dibujo en AutoCAD, pégalo en un ARCHIVO NUEVO y guarda ese como DXF 2013.")
                st.stop()
            
            msp = doc.modelspace()
            doc_3d = ezdxf.new('R2010')
            msp_3d = doc_3d.modelspace()
            
            count = 0
            # Intentamos sacar lo que sea: LINE, LWPOLYLINE, POLYLINE e incluso CIRCLE
            for entity in msp.query('LINE LWPOLYLINE POLYLINE'):
                try:
                    if entity.dxftype() == 'LINE':
                        msp_3d.add_line(entity.dxf.start, entity.dxf.end, dxfattribs={'thickness': altura_muro})
                        count += 1
                    elif entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                        pts = entity.get_points()
                        for i in range(len(pts)-1):
                            msp_3d.add_line(pts[i][:2], pts[i+1][:2], dxfattribs={'thickness': altura_muro})
                        count += 1
                except:
                    continue
            
            if count > 0:
                # La descarga debe ser BINARIA para que Streamlit no se queje
                out_buffer = io.StringIO()
                doc_3d.write(out_buffer)
                final_data = out_buffer.getvalue().encode('utf-8')
                
                st.success(f"¡RESUCITADO! Hemos extraído {count} líneas del archivo.")
                st.download_button("📥 Descargar Modelo 3D", final_data, "modelo_ia.dxf")
            else:
                st.error("Archivo leído, pero está vacío de líneas. ¿Están las paredes en capas bloqueadas?")
                
        except Exception as e:
            st.error(f"Error en el motor 2.5: {e}")

st.divider()
st.caption("ARCH-IA v2.5 | Filtrado de carácteres no-ASCII y flujo BytesIO.")
