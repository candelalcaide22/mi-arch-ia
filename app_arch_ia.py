import streamlit as st
import ezdxf
import io

# 1. Configuración de la interfaz
st.set_page_config(page_title="ARCH-IA 1.3", page_icon="🏗️")
st.title("🏗️ ARCH-IA 1.3 - SOLUCIÓN BINARIA")
st.subheader("Conversor Inteligente de Planos a 3D")

# 2. Panel lateral
st.sidebar.header("Configuración")
altura_muro = st.sidebar.slider("Altura del muro (m)", 1.0, 10.0, 2.5)

# 3. Interfaz de carga
formato = st.radio("Selecciona formato:", ("AutoCAD (.dxf)", "Nube de puntos (.xyz)"))
uploaded_file = st.file_uploader("Sube tu archivo", type=["dxf", "xyz"])

def procesar_dxf(file):
    # LEER: Usamos BytesIO para manejar el archivo como datos binarios puros
    # Esto es lo más seguro para evitar el error de 'str'
    input_stream = io.BytesIO(file.read())
    doc = ezdxf.read(input_stream)
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

# 4. Lógica de ejecución y descarga
if uploaded_file is not None:
    with st.spinner('Procesando geometría...'):
        try:
            nombre = uploaded_file.name.lower()
            if nombre.endswith('.dxf'):
                resultado = procesar_dxf(uploaded_file)
            else:
                st.error("Por favor, usa un archivo .dxf")
                st.stop()
            
            # --- LA CLAVE ESTÁ AQUÍ ---
            # En lugar de .write(), usamos .write() pero sobre un buffer de BYTES
            # 'write' en ezdxf puede escribir en streams binarios directamente
            output_buffer = io.BytesIO()
            resultado.write(output_buffer)
            datos_finales = output_buffer.getvalue()
            
            st.success("¡CONSEGUIDO! ARCH-IA ha vencido al error.")
            st.download_button(
                label="📥 Descargar Modelo 3D",
                data=datos_finales,
                file_name="ARCH_IA_MODELO_3D.dxf",
                mime="application/dxf"
            )
        except Exception as e:
            st.error(f"Error detectado: {e}")

st.divider()
st.caption("ARCH-IA v1.3 | Flujo binario directo activado.")

