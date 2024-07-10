import streamlit as st
import os


def add_logo():
    """
    Add logo to the sidebar, above multipage selection
    """
    path = '/'.join(os.path.dirname(__file__).split('/')[:-2])
    logo_path = os.path.join(path, "image/Text2Alpha_icon.png")
    st.markdown(
        f"""
        <style>
            [data-testid="stSidebarNav"] {{
                background-image: url({logo_path});
                background-repeat: no-repeat;
                background-position: 20px 20px;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    