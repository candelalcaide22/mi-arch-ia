import streamlit as st
import ezdxf
import io

# 1. Configuración de la interfaz
st.set_page_config(page_title="ARCH-IA 1.9", page_icon="🏗️")
st.title("🏗️ ARCH-IA 1.9 - COMPATIBILIDAD FORZADA")
st.subheader("Conversor Inteligente de Planos a 3D")

# 2. Panel lateral
st.sidebar.header("Configuración")
altura_muro = st.sidebar.slider("Altura del muro (m)", 1.0, 10.0, 2.5)

# 3. Interfaz de carga
uploaded_file = st.file_uploader("Sube tu archivo .dxf", type=["dxf"])

def procesar_dxf_v19(file):
    # Leemos todo el archivo
    data = file.read()
    
    # INTENTO 1: Leer como archivo normal
    try:
        return ezdxf.read(io.BytesIO(data))
    except:
        pass

    # INTENTO 2: Si es binario, intentamos "limpiar" la cabecera y forzar lectura
    try:
        # Buscamos el inicio real de las entidades para saltar errores binarios
        text_content = data.decode('latin-1', errors='ignore')
        # Buscamos donde empieza el dibujo real
        if "SECTION" in text_content:
            text_content = text_content[text_content.find("0\nSECTION"):]
        
        return ezdxf.read(io.StringIO(text_content))
    except Exception as e:
        raise Exception(f"Error crítico de formato: {e}")

# 4. Lógica de ejecución
if uploaded_file is not None:
    with st.spinner('Desencriptando archivo...'):
        try:
            doc_original = procesar_dxf_v19(uploaded_file)
            msp = doc_original.modelspace()
            
            # Crear nuevo documento 3D
            doc_3d = ezdxf.new('R2010')
            msp_3d = doc_3d.modelspace()
            
            # Extraer geometría
            for entity in msp.query('LINE LWPOLYLINE'):
                if entity.dxftype() == 'LINE':
                    msp_3d.add_line(entity.dxf.start, entity.dxf.end, dxfattribs={'thickness': altura_muro})
                elif entity.dxftype() == 'LWPOLYLINE':
                    p = entity.get_points()
                    for i in range(len(p)-1):
                        msp_3d.add_line(p[i][:2], p[i+1][:2], dxfattribs={'thickness': altura_muro})
            
            # Guardar resultado final
            out = io.StringIO()
            doc_3d.write(out)
            st.success("¡LO TENEMOS! Hemos saltado el bloqueo del archivo.")
            st.download_button("📥 Descargar Modelo 3D", out.getvalue().encode('utf-8'), "modelo_3d.dxf")
            
        except Exception as e:
            st.error(f"Sigue fallando: {e}")
            st.info("Prueba a subir un DXF guardado como 'AutoCAD 2010' o '2013'.")

st.divider()
st.caption("ARCH-IA v1.9 | Si sale v1.9 en el título, el código es el último.")
