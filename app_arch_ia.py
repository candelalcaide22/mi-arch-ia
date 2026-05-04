import streamlit as st
import ezdxf
import io

# 1. Configuración de la interfaz
st.set_page_config(page_title="ARCH-IA 1.5", page_icon="🏗️")
st.title("🏗️ ARCH-IA 1.5 - REPARACIÓN DE DATOS")
st.subheader("Conversor Inteligente de Planos a 3D")

# 2. Panel lateral
st.sidebar.header("Configuración")
altura_muro = st.sidebar.slider("Altura del muro (m)", 1.0, 10.0, 2.5)

# 3. Interfaz de carga
uploaded_file = st.file_uploader("Sube tu archivo AutoCAD (.dxf)", type=["dxf"])

def procesar_dxf_blindado(file):
    # LEER: Leemos el contenido bruto
    raw_data = file.read()
    
    try:
        # INTENTO 1: Leer como stream de bytes (estándar moderno)
        stream = io.BytesIO(raw_data)
        doc = ezdxf.read(stream)
    except Exception:
        try:
            # INTENTO 2: Si hay "datos binarios inválidos", forzamos decodificación técnica
            # Esto limpia caracteres extraños que causan el error en la línea 9304
            text_data = raw_data.decode('latin-1', errors='ignore')
            doc = ezdxf.readstr(text_data)
        except Exception as e:
            raise Exception(f"El archivo DXF está corrupto o protegido: {e}")
    
    msp = doc.modelspace()
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
    with st.spinner('Reparando y convirtiendo plano...'):
        try:
            resultado = procesar_dxf_blindado(uploaded_file)
            
            # EXPORTACIÓN SEGURA
            out_buffer = io.StringIO()
            resultado.write(out_buffer)
            final_data = out_buffer.getvalue().encode('utf-8')
            
            st.success("¡CONSEGUIDO! El error de datos binarios ha sido ignorado.")
            st.download_button(
                label="📥 Descargar Modelo 3D",
                data=final_data,
                file_name="ARCH_IA_REPARADO.dxf",
                mime="application/dxf"
            )
        except Exception as e:
            st.error(f"Error técnico persistente: {e}")
            st.info("Consejo: Intenta abrir el archivo en AutoCAD y 'Guardar como' DXF versión 2010 o 2013.")

st.divider()
st.caption("ARCH-IA v1.5 | Sistema de limpieza de datos activado.")

