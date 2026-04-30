import streamlit as st
import numpy as np
import ezdxf
import os

# Configuración de la página
st.set_page_config(page_title="ARCH-IA 1.0", layout="centered")

st.title("🏗️ ARCH-IA 1.0")
st.subheader("Conversor Inteligente de Planos 2D a 3D")

# Manual de instrucciones en la interfaz
with st.expander("📖 Instrucciones de uso"):
    st.write("""
    1. Sube tu archivo **.xyz** con las coordenadas del plano.
    2. Ajusta la **altura** y el **grosor** de los muros.
    3. Haz clic en **'Generar 3D'** y descarga tu archivo para AutoCAD.
    """)

# Barra lateral para parámetros
st.sidebar.header("Configuración del Modelo")
altura_muro = st.sidebar.slider("Altura del muro (m)", 1.0, 5.0, 2.5)
grosor_muro = st.sidebar.slider("Grosor del muro (m)", 0.1, 0.5, 0.2)

# Subida de archivo
uploaded_file = st.file_uploader("Sube tu plano (.xyz)", type=["xyz"])

if uploaded_file is not None:
    if st.button("🚀 Generar Estructura 3D"):
        # Procesamiento
        data = np.loadtxt(uploaded_file)
        pts = data[:, :2]
        
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        
        # Algoritmo de unión de ARCH-IA
        for i in range(len(pts) - 1):
            p1, p2 = pts[i], pts[i+1]
            dist = np.linalg.norm(p2 - p1)
            
            if dist < 2.0:
                v = p2 - p1
                v_norm = v / dist
                perp = np.array([-v_norm[1], v_norm[0]]) * (grosor_muro / 2)
                
                b1, b2, b3, b4 = p1+perp, p1-perp, p2-perp, p2+perp
                
                caras = [
                    [(b1[0], b1[1], 0), (b4[0], b4[1], 0), (b4[0], b4[1], altura_muro), (b1[0], b1[1], altura_muro)],
                    [(b2[0], b2[1], 0), (b3[0], b3[1], 0), (b3[0], b3[1], altura_muro), (b2[0], b2[1], altura_muro)],
                    [(b1[0], b1[1], 0), (b2[0], b2[1], 0), (b3[0], b3[1], 0), (b4[0], b4[1], 0)],
                    [(b1[0], b1[1], altura_muro), (b2[0], b2[1], altura_muro), (b3[0], b3[1], altura_muro), (b4[0], b4[1], altura_muro)]
                ]
                for c in caras: msp.add_3dface(c)
        
        # Guardar temporalmente
        output_path = "proyecto_3d.dxf"
        doc.saveas(output_path)
        
        with open(output_path, "rb") as file:
            st.download_button(
                label="📥 Descargar Plano 3D para AutoCAD",
                data=file,
                file_name="ARCH_IA_PROYECTO.dxf",
                mime="application/dxf"
            )
        st.success("¡Estructura generada con éxito!")