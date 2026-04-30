import streamlit as st
import ezdxf
import numpy as np
import io

st.set_page_config(page_title="ARCH-IA 1.0", page_icon="🏗️")

st.title("🏗️ ARCH-IA 1.0")
st.subheader("Conversor Inteligente de Planos a 3D")

# Configuración en la barra lateral
st.sidebar.header("Configuración del Modelo")
altura_muro = st.sidebar.slider("Altura del muro (m)", 1.0, 10.0, 2.5)
grosor_muro = st.sidebar.slider("Grosor del muro (m)", 0.05, 1.0, 0.2)

# Selector de formato
formato = st.radio("Selecciona el formato de entrada:", ("AutoCAD (.dxf)", "Nube de puntos (.xyz)"))

uploaded_file = st.file_uploader(f"Sube tu archivo {formato}", type=[formato[-4:].strip(".")])

def procesar_dxf(file):
    # Leer el archivo DXF subido
    content = file.read().decode("utf-8", errors="ignore")
    doc = ezdxf.readstr(content)
    msp = doc.modelspace()
    
    # Crear un nuevo DXF para el 3D
    doc_3d = ezdxf.new('R2010')
    msp_3d = doc_3d.modelspace()
    
    # Buscar líneas y polilíneas para extruirlas
    for entity in msp.query('LINE LWPOLYLINE'):
        if entity.dxftype() == 'LINE':
            start = entity.dxf.start
            end = entity.dxf.end
            # Crear caras 3D (simplificado como líneas con elevación para este ejemplo)
            msp_3d.add_line(start, end, dxfattribs={'thickness': altura_muro})
        elif entity.dxftype() == 'LWPOLYLINE':
            points = entity.get_points()
            for i in range(len(points)-1):
                msp_3d.add_line(points[i], points[i+1], dxfattribs={'thickness': altura_muro})
    
    return doc_3d

def procesar_xyz(file):
    # Lógica que ya tenías para leer puntos y crear muros
    doc_3d = ezdxf.new('R2010')
    msp_3d = doc_3d.modelspace()
    content = file.read().decode("utf-8").splitlines()
    puntos = [list(map(float, line.split())) for line in content if line.strip()]
    
    for i in range(len(puntos)-1):
        msp_3d.add_line(puntos[i], puntos[i+1], dxfattribs={'thickness': altura_muro})
    return doc_3d

if uploaded_file is not None:
    with st.spinner('Generando modelo 3D...'):
        try:
            if "dxf" in uploaded_file.name.lower():
                resultado = procesar_dxf(uploaded_file)
            else:
                resultado = procesar_xyz(uploaded_file)
            
            # Guardar en memoria para descarga
            out_buffer = io.StringIO()
            resultado.write(out_buffer)
            
            st.success("¡Modelo 3D generado con éxito!")
            st.download_button(
                label="Descargar Modelo 3D (.dxf)",
                data=out_buffer.getvalue(),
                file_name="modelo_3d_arch_ia.dxf",
                mime="application/dxf"
            )
        except Exception as e:
            st.error(f"Error al procesar: {e}")

st.info("Próximamente: Soporte para imágenes JPG/PNG y detección de ventanas.")
