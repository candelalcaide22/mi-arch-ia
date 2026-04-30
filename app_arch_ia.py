import streamlit as st
import ezdxf
import io

# Configuración de página
st.set_page_config(page_title="ARCH-IA 1.0", page_icon="🏗️")

st.title("🏗️ ARCH-IA 1.0")
st.subheader("Conversor Inteligente de Planos a 3D")

# Configuración en la barra lateral
st.sidebar.header("Configuración del Modelo")
altura_muro = st.sidebar.slider("Altura del muro (m)", 1.0, 10.0, 2.5)

# Selector de formato
formato = st.radio("Selecciona el formato de entrada:", ("AutoCAD (.dxf)", "Nube de puntos (.xyz)"))

uploaded_file = st.file_uploader(f"Sube tu archivo {formato}", type=["dxf", "xyz"])

def procesar_dxf(file):
    # Intentar leer el archivo con diferentes codificaciones
    bytes_data = file.read()
    try:
        content = bytes_data.decode("utf-8")
    except UnicodeDecodeError:
        content = bytes_data.decode("latin-1")
    
    doc = ezdxf.readstr(content)
    msp = doc.modelspace()
    
    # Crear un nuevo DXF para el 3D
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

def procesar_xyz(file):
    doc_3d = ezdxf.new('R2010')
    msp_3d = doc_3d.modelspace()
    # Leer líneas, ignorar vacías
    lines = file.read().decode("utf-8").splitlines()
    puntos = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            puntos.append((float(parts[0]), float(parts[1])))
    
    for i in range(len(puntos)-1):
        msp_3d.add_line(puntos[i], puntos[i+1], dxfattribs={'thickness': altura_muro})
    return doc_3d

if uploaded_file is not None:
    with st.spinner('Generando modelo 3D...'):
        try:
            # Identificar por extensión de nombre
            nombre = uploaded_file.name.lower()
            if nombre.endswith('.dxf'):
                resultado = procesar_dxf(uploaded_file)
            elif nombre.endswith('.xyz'):
                resultado = procesar_xyz(uploaded_file)
            else:
                st.error("Formato no soportado.")
                st.stop()
            
            # Exportar a memoria
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
            st.error(f"Error técnico: {e}")

st.info("Próximamente: Soporte para imágenes JPG/PNG y detección de ventanas.")
