import streamlit as st
import ezdxf
import io

# 1. Configuración de la interfaz
st.set_page_config(page_title="ARCH-IA 3.0", page_icon="🏗️")
st.title("🏗️ ARCH-IA 3.0 - VERSIÓN FINAL")

# 2. Panel lateral
st.sidebar.header("Configuración")
altura_muro = st.sidebar.slider("Altura de muros (m)", 1.0, 10.0, 2.5)

# 3. Cargador de archivos
uploaded_file = st.file_uploader("Sube tu archivo .dxf", type=["dxf"])

if uploaded_file is not None:
    with st.spinner('Procesando...'):
        try:
            # LEER: Leemos el archivo en modo "bruto"
            bytes_data = uploaded_file.read()
            
            # FILTRO RADICAL: 
            # Solo permitimos caracteres que existen en un teclado normal (ASCII)
            # Esto elimina CUALQUIER error binario en cualquier línea.
            clean_content = "".join([chr(b) for b in bytes_data if b < 128])
            
            # Cargamos el documento usando un método que no depende de readstr
            doc = ezdxf.read(io.StringIO(clean_content))
            msp = doc.modelspace()
            
            # Crear el nuevo documento 3D
            doc_3d = ezdxf.new('R2010')
            msp_3d = doc_3d.modelspace()
            
            count = 0
            # Buscamos líneas y polilíneas
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
                st.success(f"¡CONSEGUIDO! Se han rescatado {count} elementos.")
                st.download_button("📥 Descargar Modelo 3D", out_buffer.getvalue(), "modelo_3d.dxf")
            else:
                st.error("Archivo leído pero está vacío. Dibuja algo nuevo en AutoCAD.")

        except Exception as e:
            st.error(f"Error técnico: {e}")

st.divider()
st.caption("ARCH-IA v3.0 | Filtro de caracteres ASCII forzado.")
