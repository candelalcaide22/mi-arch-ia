import streamlit as st
import ezdxf
import io

# 1. Configuración visual de la plataforma
st.set_page_config(page_title="ARCH-IA 1.0", page_icon="🏗️")

st.title("🏗️ ARCH-IA 1.0")
st.subheader("Conversor Inteligente de Planos a 3D")

# 2. Panel lateral de control
st.sidebar.header("Configuración del Modelo")
altura_muro = st.sidebar.slider("Altura del muro (m)", 1.0, 10.0, 2.5)

# 3. Interfaz de usuario
formato = st.radio("Selecciona el formato de tu plano original:", ("AutoCAD (.dxf)", "Nube de puntos (.xyz)"))
uploaded_file = st.file_uploader(f"Arrastra aquí tu archivo {formato}", type=["dxf", "xyz"])

def procesar_dxf(file):
    # BLINDAJE ACTUALIZADO: Leer como stream de texto directamente
    # Esto evita el uso de 'readstr' que da error
    bytes_data = file.read()
    try:
        content = bytes_data.decode("utf-8")
    except UnicodeDecodeError:
        content = bytes_data.decode("latin-1")
    
    # Usamos io.StringIO para que ezdxf lo lea como un archivo de texto abierto
    stream = io.StringIO(content)
    doc = ezdxf.read(stream)
    msp = doc.modelspace()
    
    # Crear el lienzo 3D
    doc_3d = ezdxf.new('R2010')
    msp_3d = doc_3d.modelspace()
    
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
    lines = file.read().decode("utf-8").splitlines()
    puntos = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            puntos.append((float(parts[0]), float(parts[1])))
    
    for i in range(len(puntos)-1):
        msp_3d.add_line(puntos[i], puntos[i+1], dxfattribs={'thickness': altura_muro})
    return doc_3d

# 4. Lógica de ejecución
if uploaded_file is not None:
    with st.spinner('Transformando plano 2D en modelo 3D...'):
        try:
            nombre_archivo = uploaded_file.name.lower()
            
            if nombre_archivo.endswith('.dxf'):
                resultado = procesar_dxf(uploaded_file)
            elif nombre_archivo.endswith('.xyz'):
                resultado = procesar_xyz(uploaded_file)
            else:
                st.error("Formato no reconocido.")
                st.stop()
            
            # Exportar a un buffer de texto
            out_buffer = io.StringIO()
            resultado.write(out_buffer)
            
            st.success("¡Éxito! Tu modelo 3D está listo.")
            st.download_button(
                label="📥 Descargar Modelo 3D (.dxf)",
                data=out_buffer.getvalue(),
                file_name="ARCH_IA_MODELO_3D.dxf",
                mime="application/dxf"
            )
        except Exception as e:
            st.error(f"Se ha producido un error técnico: {e}")

st.divider()
st.caption("ARCH-IA v1.0 | Desarrollado para optimizar el flujo de trabajo arquitectónico.")
