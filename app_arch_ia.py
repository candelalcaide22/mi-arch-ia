import streamlit as st
import ezdxf
import io

# 1. Configuración de la interfaz
st.set_page_config(page_title="ARCH-IA 1.2", page_icon="🏗️")
st.title("🏗️ ARCH-IA 1.2 - VERSIÓN ANTIBUGS")
st.subheader("Conversor Inteligente de Planos a 3D")

# 2. Panel lateral
st.sidebar.header("Configuración")
altura_muro = st.sidebar.slider("Altura del muro (m)", 1.0, 10.0, 2.5)

# 3. Interfaz de carga
formato = st.radio("Selecciona formato:", ("AutoCAD (.dxf)", "Nube de puntos (.xyz)"))
uploaded_file = st.file_uploader("Sube tu archivo", type=["dxf", "xyz"])

def procesar_dxf(file):
    # Leer el archivo original
    stream = io.BytesIO(file.read())
    doc = ezdxf.read(stream)
    msp = doc.modelspace()
    
    # Crear nuevo documento 3D
    doc_3d = ezdxf.new('R2010')
    msp_3d = doc_3d.modelspace()
    
    # Extraer líneas y polilíneas
    for entity in msp.query('LINE LWPOLYLINE'):
        if entity.dxftype() == 'LINE':
            start = entity.dxf.start
            end = entity.dxf.end
            msp_3d.add_line(start, end, dxfattribs={'thickness': altura_muro})
        elif entity.dxftype() == 'LWPOLYLINE':
            points = entity.get_points()
            for i in range(len(points)-1):
                p1 = points[i]
                p2 = points[i+1]
                msp_3d.add_line(p1[:2], p2[:2], dxfattribs={'thickness': altura_muro})
    
    return doc_3d

# 4. Lógica de ejecución y descarga
if uploaded_file is not None:
    with st.spinner('Procesando...'):
        try:
            nombre = uploaded_file.name.lower()
            if nombre.endswith('.dxf'):
                resultado = procesar_dxf(uploaded_file)
            else:
                # Procesar XYZ básico
                resultado = ezdxf.new('R2010')
                st.warning("El modo XYZ está en mantenimiento, usa DXF preferiblemente.")
            
            # --- LA SOLUCIÓN FINAL: DOBLE CONVERSIÓN ---
            # 1. Escribimos el resultado a un buffer de texto plano
            text_stream = io.StringIO()
            resultado.write(text_stream)
            dxf_string = text_stream.getvalue()
            
            # 2. Convertimos ese texto manualmente a bytes (UTF-8)
            # Esto es lo que Streamlit exige para el download_button
            dxf_bytes = dxf_string.encode('utf-8')
            
            st.success("¡CONSEGUIDO! El archivo está listo.")
            st.download_button(
                label="📥 Descargar Modelo 3D",
                data=dxf_bytes,
                file_name="ARCH_IA_FINAL.dxf",
                mime="application/dxf"
            )
        except Exception as e:
            st.error(f"Error técnico: {e}")

st.divider()
st.caption("ARCH-IA v1.2 | Si ves 'v1.2' en el título, es que has actualizado bien.")

