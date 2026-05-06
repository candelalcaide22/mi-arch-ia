import streamlit as st
import ezdxf
import io

# 1. Configuración de la interfaz
st.set_page_config(page_title="ARCH-IA 2.0", page_icon="🏗️")
st.title("🏗️ ARCH-IA 2.0 - ÚLTIMO RECURSO")
st.subheader("Conversor Inteligente de Planos a 3D")

# 2. Panel lateral
st.sidebar.header("Configuración")
altura_muro = st.sidebar.slider("Altura del muro (m)", 1.0, 10.0, 2.5)

# 3. Interfaz de carga
uploaded_file = st.file_uploader("Sube tu archivo .dxf", type=["dxf"])

def procesar_archivo_blindado(file):
    # Leemos el archivo completo como bytes
    blob = file.read()
    
    # INTENTO A: Lectura directa (Si el archivo está bien)
    try:
        return ezdxf.read(io.BytesIO(blob))
    except:
        pass
    
    # INTENTO B: El archivo es binario o tiene basura al inicio
    # Buscamos el marcador "SECTION" que indica donde empieza el dibujo real
    try:
        # Probamos varias decodificaciones hasta encontrar texto legible
        for codec in ['utf-8', 'latin-1', 'cp1252']:
            try:
                texto = blob.decode(codec, errors='ignore')
                if "SECTION" in texto:
                    # Cortamos todo lo que haya antes del primer marcador de AutoCAD
                    inicio_real = texto.find("0\nSECTION")
                    if inicio_real == -1: inicio_real = texto.find("0\r\nSECTION")
                    
                    if inicio_real != -1:
                        nuevo_texto = texto[inicio_real:]
                        return ezdxf.read(io.StringIO(nuevo_texto))
            except:
                continue
    except Exception as e:
        raise Exception("El formato del archivo es incompatible. No es un DXF de texto estándar.")

# 4. Lógica de ejecución
if uploaded_file is not None:
    with st.spinner('Descriptando estructura binaria...'):
        try:
            doc_original = procesar_archivo_blindado(uploaded_file)
            if not doc_original:
                st.error("No se pudo interpretar el archivo. Asegúrate de que no es un .dwg renombrado.")
                st.stop()
                
            msp = doc_original.modelspace()
            doc_3d = ezdxf.new('R2010')
            msp_3d = doc_3d.modelspace()
            
            # Buscamos líneas y polilíneas para extruir
            # Añadimos 'POLYLINE' por si acaso
            for entity in msp.query('LINE LWPOLYLINE POLYLINE'):
                if entity.dxftype() == 'LINE':
                    msp_3d.add_line(entity.dxf.start, entity.dxf.end, dxfattribs={'thickness': altura_muro})
                elif entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                    p = entity.get_points()
                    for i in range(len(p)-1):
                        msp_3d.add_line(p[i][:2], p[i+1][:2], dxfattribs={'thickness': altura_muro})
            
            # Exportación final forzada a UTF-8
            out = io.StringIO()
            doc_3d.write(out)
            byte_data = out.getvalue().encode('utf-8', errors='ignore')
            
            st.success("¡LO HEMOS LOGRADO! Archivo recuperado y procesado.")
            st.download_button("📥 Descargar Modelo 3D", byte_data, "resultado_3d.dxf")
            
        except Exception as e:
            st.error(f"Error crítico: {e}")
            st.info("💡 Si esto falla, el archivo NO es un DXF. Prueba a subir otro archivo diferente.")

st.divider()
st.caption("ARCH-IA v2.0 | Si ves v2.0, estás en la versión de rescate extremo.")
