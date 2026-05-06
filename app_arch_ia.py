import streamlit as st
import ezdxf
import io

# 1. Configuración de la interfaz
st.set_page_config(page_title="ARCH-IA 2.3", page_icon="🏗️")
st.title("🏗️ ARCH-IA 2.3 - MODO BISTURÍ")
st.subheader("Conversor Inteligente de Planos a 3D")

# 2. Panel lateral
st.sidebar.header("Configuración")
altura_muro = st.sidebar.slider("Altura del muro (m)", 1.0, 10.0, 2.5)

# 3. Interfaz de carga
uploaded_file = st.file_uploader("Sube tu archivo .dxf", type=["dxf"])

def limpiar_y_leer_dxf(file):
    # Leemos el archivo completo como bytes
    data = file.read()
    
    # Decodificamos a texto (siendo muy permisivos con los errores)
    try:
        texto = data.decode('latin-1', errors='ignore')
    except Exception as e:
        st.error(f"Error al leer el texto del archivo: {e}")
        return None

    # BUSQUEDA ESTRATÉGICA: AutoCAD DXF siempre empieza con un 0 y SECTION
    # A veces hay basura al principio (metadatos de AutoCAD) que rompe todo.
    if "SECTION" in texto:
        # Buscamos la primera aparición de 0 seguido de SECTION
        # Probamos con diferentes finales de línea (\n y \r\n)
        pos = texto.find("0\nSECTION")
        if pos == -1: pos = texto.find("0\r\nSECTION")
        
        if pos != -1:
            texto_limpio = texto[pos:] # Cortamos la basura del principio
            try:
                # Intentamos leer el texto limpio
                return ezdxf.read(io.StringIO(texto_limpio))
            except Exception as e:
                st.warning(f"Fallo al leer tras limpiar cabecera: {e}")
    
    # Intento final: lectura estándar si lo anterior no funcionó
    try:
        return ezdxf.read(io.BytesIO(data))
    except Exception as e:
        st.error(f"La librería no reconoce el formato: {e}")
        return None

# 4. Lógica de ejecución
if uploaded_file is not None:
    with st.spinner('Operando el archivo...'):
        try:
            doc = limpiar_y_leer_dxf(uploaded_file)
            
            if doc is None:
                st.stop()
            
            msp = doc.modelspace()
            doc_3d = ezdxf.new('R2010')
            msp_3d = doc_3d.modelspace()
            
            # Buscamos líneas y polilíneas
            count = 0
            for entity in msp.query('LINE LWPOLYLINE POLYLINE'):
                if entity.dxftype() == 'LINE':
                    msp_3d.add_line(entity.dxf.start, entity.dxf.end, dxfattribs={'thickness': altura_muro})
                    count += 1
                elif entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                    pts = entity.get_points()
                    for i in range(len(pts)-1):
                        msp_3d.add_line(pts[i][:2], pts[i+1][:2], dxfattribs={'thickness': altura_muro})
                    count += 1
            
            if count == 0:
                st.warning("No se encontraron líneas o polilíneas en el plano. Asegúrate de que no son bloques o capas ocultas.")
            else:
                # Preparar descarga
                out = io.StringIO()
                doc_3d.write(out)
                st.success(f"¡CONSEGUIDO! Se han procesado {count} elementos.")
                st.download_button("📥 Descargar Resultado 3D", out.getvalue().encode('utf-8'), "arch_ia_3d.dxf")
            
        except Exception as e:
            st.error(f"Error crítico en el proceso: {e}")

st.divider()
st.caption("ARCH-IA v2.3 | Limpiando cabeceras corruptas en archivos ASCII.")
