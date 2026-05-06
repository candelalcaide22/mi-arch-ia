import streamlit as st
import ezdxf
import io
import re

# 1. Configuración de la interfaz
st.set_page_config(page_title="ARCH-IA 1.8", page_icon="🏗️")
st.title("🏗️ ARCH-IA 1.8 - FILTRO ANTIBINARIO")
st.subheader("Conversor Inteligente de Planos a 3D")

# 2. Panel lateral
st.sidebar.header("Configuración")
altura_muro = st.sidebar.slider("Altura del muro (m)", 1.0, 10.0, 2.5)

# 3. Interfaz de carga
uploaded_file = st.file_uploader("Sube tu archivo AutoCAD (.dxf)", type=["dxf"])

def limpiar_dxf_binario(raw_bytes):
    """
    Intenta limpiar caracteres no imprimibles que causan el error 9304
    antes de pasar el archivo a ezdxf.
    """
    # Intentamos decodificar ignorando errores para obtener texto puro
    text = raw_bytes.decode('latin-1', errors='ignore')
    # Eliminamos caracteres de control extraños (excepto saltos de línea y retornos)
    text_limpio = "".join(i for i in text if ord(i) < 128 or i in '\n\r\t')
    return text_limpio

def procesar_dxf_v18(file):
    raw_data = file.read()
    
    # PASO 1: Limpieza manual del texto
    texto_procesado = limpiar_dxf_binario(raw_data)
    
    # PASO 2: Cargar el documento desde el texto limpio
    stream = io.StringIO(texto_procesado)
    doc = ezdxf.read(stream)
    msp = doc.modelspace()
    
    # Crear nuevo documento 3D
    doc_3d = ezdxf.new('R2010')
    msp_3d = doc_3d.modelspace()
    
    # Procesar geometrías
    for entity in msp.query('LINE LWPOLYLINE'):
        if entity.dxftype() == 'LINE':
            msp_3d.add_line(entity.dxf.start, entity.dxf.end, dxfattribs={'thickness': altura_muro})
        elif entity.dxftype() == 'LWPOLYLINE':
            points = entity.get_points()
            for i in range(len(points)-1):
                msp_3d.add_line(points[i][:2], points[i+1][:2], dxfattribs={'thickness': altura_muro})
    
    return doc_3d

# 4. Lógica de ejecución
if uploaded_file is not None:
    with st.spinner('Ejecutando limpieza profunda del archivo...'):
        try:
            resultado = procesar_dxf_v18(uploaded_file)
            
            # Exportación a bytes
            out_buffer = io.StringIO()
            resultado.write(out_buffer)
            final_bytes = out_buffer.getvalue().encode('utf-8', errors='ignore')
            
            st.success("¡ARCHIVO DESBLOQUEADO! Hemos saltado las líneas corruptas.")
            st.download_button(
                label="📥 Descargar Modelo 3D",
                data=final_bytes,
                file_name="ARCH_IA_FINAL_REPARADO.dxf",
                mime="application/dxf"
            )
        except Exception as e:
            st.error(f"El archivo sigue bloqueado: {e}")
            st.warning("⚠️ ÚLTIMO RECURSO: Abre el archivo en AutoCAD, dale a 'Guardar como' y asegúrate de elegir 'AutoCAD 2013 DXF (ASCII)'.")

st.divider()
st.caption("ARCH-IA v1.8 | Filtro de caracteres no-ASCII activado.")
