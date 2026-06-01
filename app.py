import streamlit as st
import login as login
import base64

st.header(':blue[Página Principal]')
login.generarLogin()
if 'usuario' in st.session_state:
    def image_to_base64(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    image_path = "C:/Programa_Python/Faturamento2024SQL/images/*******.jpg"
    image_base64 = image_to_base64(image_path)
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/jpeg;base64,{image_base64}" alt="Logo" style="width: 80%; max-width: 600px;">
            <p style="font-size: 18px; color: #333;">Sistema de CRUD em Python</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    btnSair = st.button("Sair", type="primary")
    if btnSair:
        st.session_state.clear()
        st.rerun()       
    # Footer
    #st.markdown("---")
    #st.caption(" 📊 Dashboard desenvolvido por Sérgio Renato Steglich ")
