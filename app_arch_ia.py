import streamlit as st
import ezdxf
import io

# 1. Configuración de la interfaz
st.set_page_config(page_title="ARCH-IA 2.6", page_icon="🏗️")
st.title("🏗️ ARCH-IA 2.6 - MODO COMPATIBILIDAD TOTAL")
st.subheader("Conversor Inteligente de Planos a 3D")

# 2. Panel lateral
st.sidebar.header("Configuración")
altura_muro = st.sidebar.slider("Altura de muros (m)", 1.0, 10.0, 2.5)

# 3. Interfaz de carga
uploaded_file = st.file_uploader("Sube tu archivo .dxf", type=["dxf"])

def motor_limpieza_extrema(file):
    # Leemos el archivo bruto
    raw_data = file.read()
    
    # Intentamos decodificar a texto de la forma más agresiva posible
    # Esto elimina los errores de la línea 11810 al ignorar lo que no sea texto
    try:
        text_content = raw_data.decode('latin-1', errors='ignore')
    except:
        text_content = raw_data.decode('utf-8', errors='ignore')
    
    # En lugar de 'readstr' (que da error), usamos io.StringIO
    # Esto convierte el texto en un "archivo virtual" que la librería SÍ acepta
    archivo_virtual = io.StringIO(text_content)
    
    try:
        # Usamos ezdxf.read() que es la función más estable
        return ezdxf.read(archivo_virtual)
    except Exception as e:
        st.error(f"Error de lectura en la librería: {e}")
        return None

# 4. Lógica de ejecución
if uploaded_file is not None:
    with st.spinner('Procesando archivo...'):
        try:
            doc = motor_limpieza_extrema(uploaded_file)
            
            if doc is None:
                st.stop()
            
            msp = doc.modelspace()
            doc_3d = ezdxf.new('R2010')
            msp_3d = doc_3d.modelspace()
            
            count = 0
            # Buscamos elementos básicos
            for entity in msp.query('LINE LWPOLYLINE POLYLINE'):
                try:
                    if entity.dxftype() == 'LINE':
                        msp_3d.add_line(entity.dxf.start, entity.dxf.end, dxfattribs={'thickness': altura_muro})
                        count += 1
                    elif entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                        pts = entity.get_points()
                        for i in range(len(pts)-1):
                            msp_3d.add_line(pts[i][:2], pts[i+1][:2], dxfattribs={'thickness': altura_muro})
                        count += 1
                except:
                    continue
            
            if count > 0:
                # Generamos el archivo de salida
                salida_texto = io.StringIO()
                doc_3d.write(salida_texto)
                
                # Convertimos a bytes para que el botón de descarga no falle
                datos_finales = salida_texto.getvalue().encode('utf-8')
                
                st.success(f"¡CONSEGUIDO! Se han rescatado {count} líneas.")
                st.download_button(
                    label="📥 Descargar Modelo 3D",
                    data=datos_finales,
                    file_name="resultado_arch_ia.dxf",
                    mime="application/dxf"
                )
            else:
                st.warning("No se encontraron líneas procesables. Revisa que no sean bloques.")
                
        except Exception as e:
            st.error(f"Error crítico en v2.6: {e}")

st.divider()
st.caption("ARCH-IA v2.6 | Sin funciones obsoletas y con bypass de StringIO.")
