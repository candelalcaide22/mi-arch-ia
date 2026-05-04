import streamlit as st
import ezdxf
import io

# 1. Configuración de la interfaz
st.set_page_config(page_title="ARCH-IA 1.6", page_icon="🏗️")
st.title("🏗️ ARCH-IA 1.6 - MODO COMPATIBILIDAD TOTAL")
st.subheader("Conversor Inteligente de Planos a 3D")

# 2. Panel lateral
st.sidebar.header("Configuración")
altura_muro = st.sidebar.slider("Altura del muro (m)", 1.0, 10.0, 2.5)

# 3. Interfaz de carga
uploaded_file = st.file_uploader("Sube tu archivo AutoCAD (.dxf)", type=["dxf"])

def procesar_dxf_final(file):
    # LEER: Obtenemos los datos brutos
    raw_data = file.read()
    
    # Intentamos decodificar a texto ignorando basura binaria (adiós error 9304)
    # latin-1 es el formato que mejor "traga" los errores de AutoCAD
    text_cleaned = raw_data.decode('latin-1', errors='ignore')
    
    # Creamos un "archivo virtual" de texto
    # Esto sustituye a 'readstr' de forma oficial
    text_stream = io.StringIO(text_cleaned)
    
    # Cargamos el documento
    doc = ezdxf.read(text_stream)
    msp = doc.modelspace()
    
    # Crear nuevo documento 3D
    doc_3d = ezdxf.new('R2010')
    msp_3d = doc_3d.modelspace()
    
    # Procesar geometrías
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
                # Forzamos 2D para asegurar la base antes de extruir
                msp_3d.add_line(p1[:2], p2[:2], dxfattribs={'thickness': altura_muro})
    
    return doc_3d

# 4. Lógica de ejecución
if uploaded_file is not None:
    with st.spinner('Limpiando y convirtiendo...'):
        try:
            resultado = procesar_dxf_final(uploaded_file)
            
            # EXPORTACIÓN
            # Generamos el archivo final como bytes para el botón de descarga
            out_buffer = io.StringIO()
            resultado.write(out_buffer)
            byte_data = out_buffer.getvalue().encode('utf-8')
            
            st.success("¡POR FIN! El archivo ha sido procesado y limpiado.")
            st.download_button(
                label="📥 Descargar Modelo 3D",
                data=byte_data,
                file_name="ARCH_IA_MODELO_3D.dxf",
                mime="application/dxf"
            )
        except Exception as e:
            st.error(f"Error técnico persistente: {e}")

st.divider()
st.caption("ARCH-IA v1.6 | Depuración completa de funciones obsoletas.")
