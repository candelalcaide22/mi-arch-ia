import streamlit as st
import ezdxf
import io

# 1. Configuración de la interfaz
st.set_page_config(page_title="ARCH-IA 1.1", page_icon="🏗️")
st.title("🏗️ ARCH-IA 1.1 - VERSIÓN FINAL")
st.subheader("Conversor Inteligente de Planos a 3D")

# 2. Panel lateral
st.sidebar.header("Configuración")
altura_muro = st.sidebar.slider("Altura del muro (m)", 1.0, 10.0, 2.5)

# 3. Interfaz de carga
formato = st.radio("Selecciona formato:", ("AutoCAD (.dxf)", "Nube de puntos (.xyz)"))
uploaded_file = st.file_uploader("Sube tu archivo", type=["dxf", "xyz"])

def procesar_dxf(file):
    # LEER EN BINARIO (Crucial para evitar el error de 'str')
    stream = io.BytesIO(file.read())
    doc = ezdxf.read(stream)
    msp = doc.modelspace()
    
    # Crear nuevo documento 3D
    doc_3d = ezdxf.new('R2010')
    msp_3d = doc_3d.modelspace()
    
    # Procesar líneas y polilíneas
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

# 4. Lógica de ejecución y descarga
if uploaded_file is not None:
    with st.spinner('Procesando...'):
        try:
            nombre = uploaded_file.name.lower()
            if nombre.endswith('.dxf'):
                resultado = procesar_dxf(uploaded_file)
            else:
                resultado = procesar_xyz(uploaded_file)
            
            # --- LA SOLUCIÓN DEFINITIVA AL ERROR DE BYTES/STR ---
            # Forzamos la escritura directamente a un buffer de BYTES
            out_buffer = io.BytesIO()
            # Esta es la forma correcta de guardar un DXF como binario puro
            resultado.write(out_buffer) 
            byte_data = out_buffer.getvalue()
            
            st.success("¡LO TENEMOS! Descarga tu modelo ahora.")
            st.download_button(
                label="📥 Descargar Modelo 3D",
                data=byte_data,
                file_name="ARCH_IA_RESULTADO.dxf",
                mime="application/dxf"
            )
        except Exception as e:
            # Si algo falla, limpiamos el error para que sea legible
            st.error(f"Error detectado: {e}")

st.divider()
st.caption("ARCH-IA v1.1 | Código revisado para flujo binario puro.")
