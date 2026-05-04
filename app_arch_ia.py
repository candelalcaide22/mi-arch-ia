import streamlit as st
import ezdxf
import io

# 1. Configuración de la interfaz
st.set_page_config(page_title="ARCH-IA 1.0", page_icon="🏗️")
st.title("🏗️ ARCH-IA 1.0")
st.subheader("Conversor Inteligente de Planos a 3D")

# 2. Panel lateral
st.sidebar.header("Configuración")
altura_muro = st.sidebar.slider("Altura del muro (m)", 1.0, 10.0, 2.5)

# 3. Interfaz de carga
formato = st.radio("Selecciona formato:", ("AutoCAD (.dxf)", "Nube de puntos (.xyz)"))
uploaded_file = st.file_uploader(f"Sube tu archivo", type=["dxf", "xyz"])

def procesar_dxf(file):
    # LEER: Obtenemos los bytes
    blob = file.read()
    
    # Creamos un stream binario. ezdxf.read() acepta un objeto tipo archivo.
    # Esto es mucho más seguro que readstr
    stream = io.BytesIO(blob)
    
    # Intentamos leerlo. Si hay error de codificación, ezdxf suele manejarlo bien aquí.
    doc = ezdxf.read(stream)
    msp = doc.modelspace()
    
    # Nuevo documento 3D (Formato R2010 para máxima compatibilidad)
    doc_3d = ezdxf.new('R2010')
    msp_3d = doc_3d.modelspace()
    
    # Filtrar solo líneas y polilíneas
    for entity in msp.query('LINE LWPOLYLINE'):
        if entity.dxftype() == 'LINE':
            start = entity.dxf.start
            end = entity.dxf.end
            # El truco: 'thickness' eleva la línea en el eje Z
            msp_3d.add_line(start, end, dxfattribs={'thickness': altura_muro})
        elif entity.dxftype() == 'LWPOLYLINE':
            points = entity.get_points()
            for i in range(len(points)-1):
                p1 = points[i]
                p2 = points[i+1]
                # Forzamos 2D para la base y aplicamos elevación
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
            try: puntos.append((float(parts[0]), float(parts[1])))
            except: continue
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
            
            # --- SALIDA BLINDADA ---
            # Ezdxf escribe el resultado en un buffer de texto
            s_buffer = io.StringIO()
            resultado.write(s_buffer)
            datos_finales = s_buffer.getvalue()
            
            st.success("¡Hecho! Ya puedes descargar tu modelo.")
            st.download_button(
                label="📥 Descargar Resultado 3D",
                data=datos_finales,
                file_name="ARCH_IA_MODELO.dxf",
                mime="text/plain"
            )
        except Exception as e:
            st.error(f"Error detectado: {e}")

st.divider()
st.caption("ARCH-IA v1.0 | Arreglando el mundo línea a línea.")
