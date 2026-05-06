import streamlit as st
import ezdxf
import io

# 1. Configuración de la interfaz
st.set_page_config(page_title="ARCH-IA 2.4", page_icon="🏗️")
st.title("🏗️ ARCH-IA 2.4 - MODO INMUNE")
st.subheader("Conversor Inteligente de Planos a 3D")

# 2. Panel lateral
st.sidebar.header("Configuración")
altura_muro = st.sidebar.slider("Altura del muro (m)", 1.0, 10.0, 2.5)

# 3. Interfaz de carga
uploaded_file = st.file_uploader("Sube tu archivo .dxf", type=["dxf"])

def lectura_super_segura(file):
    # Leemos el archivo como bytes
    data = file.read()
    
    # INTENTO 1: Usamos la función nativa de recuperación de ezdxf
    # Esta función es como un médico de urgencias: ignora las partes rotas del archivo
    try:
        # Creamos el stream de bytes
        stream = io.BytesIO(data)
        # recover() es mucho más potente que read() para archivos con errores
        doc, auditor = ezdxf.recover.read(stream)
        return doc
    except Exception as e:
        st.warning(f"La recuperación automática falló, intentando limpieza manual...")
    
    # INTENTO 2: Limpieza manual agresiva (Solo nos quedamos con lo que sea texto puro)
    try:
        # Decodificamos ignorando CUALQUIER cosa que no sea texto
        text_data = data.decode('ascii', errors='ignore')
        # Si el archivo tiene algo de DXF, ezdxf lo encontrará aquí
        return ezdxf.readstr(text_data)
    except Exception as e:
        # Si falla el anterior, probamos con latin-1 que es más flexible
        try:
            text_data = data.decode('latin-1', errors='ignore')
            return ezdxf.readstr(text_data)
        except:
            st.error("Incluso el modo inmune ha fallado. El archivo tiene un error estructural grave.")
            return None

# 4. Lógica de ejecución
if uploaded_file is not None:
    with st.spinner('Ignorando datos corruptos y extrayendo dibujo...'):
        try:
            doc = lectura_super_segura(uploaded_file)
            
            if doc is None:
                st.stop()
            
            msp = doc.modelspace()
            doc_3d = ezdxf.new('R2010')
            msp_3d = doc_3d.modelspace()
            
            count = 0
            # Procesamos las entidades (añadimos try/except por cada línea por si acaso)
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
                    continue # Si una línea está rota, la saltamos y vamos a la siguiente
            
            if count > 0:
                out = io.StringIO()
                doc_3d.write(out)
                st.success(f"¡LOGRADO! Se han rescatado {count} elementos del archivo.")
                st.download_button("📥 Descargar Resultado 3D", out.getvalue().encode('utf-8'), "modelo_rescatado.dxf")
            else:
                st.error("No se han podido rescatar elementos. ¿Seguro que hay líneas en el dibujo?")
                
        except Exception as e:
            st.error(f"Error crítico: {e}")

st.divider()
st.caption("ARCH-IA v2.4 | Usando ezdxf.recover para saltar errores binarios.")
