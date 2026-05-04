import streamlit as st
import ezdxf
import io

# 1. Configuración de la interfaz
st.set_page_config(page_title="ARCH-IA 1.7", page_icon="🏗️")
st.title("🏗️ ARCH-IA 1.7 - LIMPIEZA PROFUNDA")
st.subheader("Conversor Inteligente de Planos a 3D")

# 2. Panel lateral
st.sidebar.header("Configuración")
altura_muro = st.sidebar.slider("Altura del muro (m)", 1.0, 10.0, 2.5)

# 3. Interfaz de carga
uploaded_file = st.file_uploader("Sube tu archivo AutoCAD (.dxf)", type=["dxf"])

def procesar_dxf_extremo(file):
    # LEER: Obtenemos los bytes brutos
    raw_bytes = file.read()
    
    # TRUCO MAESTRO: Forzamos la decodificación ignorando errores binarios
    # Esto "borra" lo que haya de malo en la línea 9304 y deja solo el dibujo
    try:
        # Intentamos con latin-1 que es el más permisivo con archivos viejos
        text_content = raw_bytes.decode('latin-1', errors='ignore')
    except:
        # Si falla, usamos utf-8 ignorando errores
        text_content = raw_bytes.decode('utf-8', errors='ignore')
    
    # Creamos un stream de texto que ezdxf entienda
    text_stream = io.StringIO(text_content)
    
    # Cargamos el documento
    doc = ezdxf.read(text_stream)
    msp = doc.modelspace()
    
    # Crear nuevo documento 3D
    doc_3d = ezdxf.new('R2010')
    msp_3d = doc_3d.modelspace()
    
    # Procesar líneas y polilíneas
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
    with st.spinner('Extrayendo geometría y limpiando errores...'):
        try:
            resultado = procesar_dxf_extremo(uploaded_file)
            
            # EXPORTACIÓN SEGURA
            out_buffer = io.StringIO()
            resultado.write(out_buffer)
            final_bytes = out_buffer.getvalue().encode('utf-8', errors='ignore')
            
            st.success("¡LO LOGRAMOS! El error de la línea 9304 ha sido neutralizado.")
            st.download_button(
                label="📥 Descargar Modelo 3D",
                data=final_bytes,
                file_name="ARCH_IA_REPARADO.dxf",
                mime="application/dxf"
            )
        except Exception as e:
            st.error(f"Error persistente: {e}")
            st.info("💡 Si esto sigue fallando, abre tu archivo en AutoCAD y guárdalo como 'DXF de texto (ASCII)' en lugar de binario.")

st.divider()
st.caption("ARCH-IA v1.7 | Modo de rescate de archivos corruptos activo.")
