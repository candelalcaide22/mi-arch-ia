import streamlit as st
import ezdxf
import io

# 1. Configuración de la interfaz
st.set_page_config(page_title="ARCH-IA 1.0", page_icon="🏗️")
st.title("🏗️ ARCH-IA 1.0")
st.subheader("Conversor Inteligente de Planos a 3D")

# 2. Parámetros laterales
st.sidebar.header("Configuración del Modelo")
altura_muro = st.sidebar.slider("Altura del muro (m)", 1.0, 10.0, 2.5)

# 3. Selección de formato
formato = st.radio("Selecciona el formato de tu plano original:", ("AutoCAD (.dxf)", "Nube de puntos (.xyz)"))
uploaded_file = st.file_uploader(f"Sube tu archivo {formato}", type=["dxf", "xyz"])

def procesar_dxf(file):
    # Paso 1: Leer el archivo como bytes
    blob = file.read()
    
    # Paso 2: Usar BytesIO para que ezdxf lo lea como un "fichero real"
    # Esto evita el error de 'readstr' y de 'bytes-like object'
    stream = io.BytesIO(blob)
    doc = ezdxf.read(stream)
    msp = doc.modelspace()
    
    # Crear el nuevo documento 3D
    doc_3d = ezdxf.new('R2010')
    msp_3d = doc_3d.modelspace()
    
    # Recorrer líneas y polilíneas
    for entity in msp.query('LINE LWPOLYLINE'):
        if entity.dxftype() == 'LINE':
            start = entity.dxf.start
            end = entity.dxf.end
            # Añadimos la extrusión con thickness
            msp_3d.add_line(start, end, dxfattribs={'thickness': altura_muro})
        elif entity.dxftype() == 'LWPOLYLINE':
            points = entity.get_points()
            for i in range(len(points)-1):
                p1 = points[i]
                p2 = points[i+1]
                # Aseguramos que solo usamos X e Y (p1[:2])
                msp_3d.add_line(p1[:2], p2[:2], dxfattribs={'thickness': altura_muro})
    
    return doc_3d

def procesar_xyz(file):
    doc_3d = ezdxf.new('R2010')
    msp_3d = doc_3d.modelspace()
    content = file.read().decode("utf-8", errors="ignore").splitlines()
    puntos = []
    for line in content:
        parts = line.split()
        if len(parts) >= 2:
            try:
                puntos.append((float(parts[0]), float(parts[1])))
            except:
                continue
    
    for i in range(len(puntos)-1):
        msp_3d.add_line(puntos[i], puntos[i+1], dxfattribs={'thickness': altura_muro})
    return doc_3d

# 4. Lógica de ejecución
if uploaded_file is not None:
    with st.spinner('Procesando geometría...'):
        try:
            nombre = uploaded_file.name.lower()
            if nombre.endswith('.dxf'):
                resultado = procesar_dxf(uploaded_file)
            else:
                resultado = procesar_xyz(uploaded_file)
            
            # Generar el buffer de salida para descargar
            out_buffer = io.StringIO()
            resultado.write(out_buffer)
            
            st.success("¡Modelo 3D generado con éxito!")
            st.download_button(
                label="📥 Descargar Resultado 3D",
                data=out_buffer.getvalue(),
                file_name="ARCH_IA_3D.dxf",
                mime="application/dxf"
            )
        except Exception as e:
            st.error(f"Error detectado: {e}")

st.divider()
st.info("💡 Consejo: Asegúrate de que el DXF no esté abierto en AutoCAD al subirlo.")
