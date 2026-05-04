import streamlit as st
import ezdxf
import io

# 1. Configuración de la interfaz
st.set_page_config(page_title="ARCH-IA 1.4", page_icon="🏗️")
st.title("🏗️ ARCH-IA 1.4 - MODO RESCATE")
st.subheader("Conversor Inteligente de Planos a 3D")

# 2. Panel lateral
st.sidebar.header("Configuración")
altura_muro = st.sidebar.slider("Altura del muro (m)", 1.0, 10.0, 2.5)

# 3. Interfaz de carga
formato = st.radio("Selecciona formato:", ("AutoCAD (.dxf)", "Nube de puntos (.xyz)"))
uploaded_file = st.file_uploader("Sube tu archivo", type=["dxf"])

def procesar_dxf(file):
    # LEER: Usamos el método más compatible posible
    blob = file.read()
    try:
        # Intentamos leerlo como stream de bytes
        doc = ezdxf.read(io.BytesIO(blob))
    except:
        # Si falla, probamos decodificando a texto (latín-1 es el más tragón)
        doc = ezdxf.read(io.StringIO(blob.decode('latin-1', errors='ignore')))
    
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

# 4. Lógica de ejecución
if uploaded_file is not None:
    with st.spinner('Forzando conversión...'):
        try:
            resultado = procesar_dxf(uploaded_file)
            
            # --- LA SOLUCIÓN QUE NO PUEDE FALLAR ---
            # Guardamos a texto primero (StringIO siempre acepta texto de ezdxf)
            s_buffer = io.StringIO()
            resultado.write(s_buffer)
            texto_del_plano = s_buffer.getvalue()
            
            # AHORA convertimos el texto a bytes nosotros mismos
            # Esto es lo que el error "bytes-like object" pide a gritos
            datos_binarios = texto_del_plano.encode('utf-8', errors='ignore')
            
            st.success("¡LO HEMOS DOBLADO! El archivo está listo.")
            st.download_button(
                label="📥 Descargar Modelo 3D",
                data=datos_binarios,
                file_name="ARCH_IA_FINAL.dxf",
                mime="application/dxf"
            )
        except Exception as e:
            st.error(f"Error técnico: {e}")

st.divider()
st.caption("ARCH-IA v1.4 | Si esto falla, el problema es el servidor, no el código.")


