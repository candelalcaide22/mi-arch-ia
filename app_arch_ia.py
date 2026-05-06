import streamlit as st
import ezdxf
import io

# 1. Configuración de la interfaz
st.set_page_config(page_title="ARCH-IA 2.9", page_icon="🏗️")
st.title("🏗️ ARCH-IA 2.9 - LIMPIEZA ATÓMICA")

# 2. Panel lateral
st.sidebar.header("Configuración")
altura_muro = st.sidebar.slider("Altura de muros (m)", 1.0, 10.0, 2.5)

# 3. Cargador de archivos
uploaded_file = st.file_uploader("Sube tu archivo .dxf", type=["dxf"])

if uploaded_file is not None:
    with st.spinner('Desintegrando errores binarios...'):
        try:
            # LEER: Leemos el archivo en modo "bruto"
            bytes_data = uploaded_file.read()
            
            # --- LIMPIEZA ATÓMICA ---
            # Filtramos el archivo byte a byte: solo dejamos caracteres de texto (ASCII)
            # Esto elimina físicamente el error de la línea 11810
            clean_bytes = bytes([b for b in bytes_data if b < 128])
            
            # Convertimos a texto seguro
            text_data = clean_bytes.decode('ascii', errors='ignore')
            
            # Cargamos el documento desde el "texto puro"
            archivo_virtual = io.StringIO(text_data)
            doc = ezdxf.read(archivo_virtual)
            msp = doc.modelspace()
            
            # Crear el nuevo documento 3D
            doc_3d = ezdxf.new('R2010')
            msp_3d = doc_3d.modelspace()
            
            count = 0
            for e in msp.query('LINE LWPOLYLINE'):
                if e.dxftype() == 'LINE':
                    msp_3d.add_line(e.dxf.start, e.dxf.end, dxfattribs={'thickness': altura_muro})
                    count += 1
                elif e.dxftype() == 'LWPOLYLINE':
                    pts = e.get_points()
                    for i in range(len(pts)-1):
                        msp_3d.add_line(pts[i][:2], pts[i+1][:2], dxfattribs={'thickness': altura_muro})
                    count += 1

            if count > 0:
                out_buffer = io.StringIO()
                doc_3d.write(out_buffer)
                st.success(f"¡POR FIN! Se han rescatado {count} líneas.")
                st.download_button("📥 Descargar Modelo 3D", out_buffer.getvalue(), "modelo_ia.dxf")
            else:
                st.error("Archivo limpio, pero no veo líneas. ¿Están en bloques?")

        except Exception as e:
            st.error(f"Error persistente: {e}")
            st.info("💡 Si esto falla, el archivo está realmente dañado. Prueba con un dibujo nuevo y simple.")

st.divider()
st.caption("ARCH-IA v2.9 | Filtrado byte a byte activado.")
