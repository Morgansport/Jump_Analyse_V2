import streamlit as st
import tempfile
import os
import imageio
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import datetime
from PIL import Image

st.set_page_config(page_title="Analyse Saut v6 - Amélioré", layout="centered")
st.title("🦘 Analyse par temps de vol (MyJump2-like)")

# Formulaire
prenom = st.text_input("Prénom")
taille_cm = st.number_input("Taille (cm)", min_value=120, max_value=230, value=203)
poids_kg = st.number_input("Poids (kg)", min_value=30, max_value=200, value=100)

uploaded_video = st.file_uploader("📹 Upload ta vidéo (MP4)", type=["mp4"])

if uploaded_video:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tfile.write(uploaded_video.read())
    video_path = tfile.name
    st.video(video_path)

    reader = imageio.get_reader(video_path)
    fps = reader.get_meta_data()["fps"]
    total_frames = reader.count_frames()

    st.markdown("🎯 Sélectionne les **images clés** du saut")
    col1, col2 = st.columns(2)
    with col1:
        frame_decollage = st.number_input("Image décollage", min_value=0, max_value=total_frames - 1, value=0, step=1)
    with col2:
        frame_atterrissage = st.number_input("Image atterrissage", min_value=0, max_value=total_frames - 1, value=total_frames - 1, step=1)

    def afficher_frame(reader, frame_num):
        try:
            frame = reader.get_data(frame_num)
            return Image.fromarray(frame)
        except:
            return None

    st.subheader("🖼️ Prévisualisation des images sélectionnées")
    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"**Décollage (image {frame_decollage})**")
        img1 = afficher_frame(reader, frame_decollage)
        if img1:
            st.image(img1, caption="Décollage")

    with col4:
        st.markdown(f"**Atterrissage (image {frame_atterrissage})**")
        img2 = afficher_frame(reader, frame_atterrissage)
        if img2:
            st.image(img2, caption="Atterrissage")

    if st.button("🚀 Lancer l'analyse"):
        t_vol = (frame_atterrissage - frame_decollage) / fps
        g = 9.81
        hauteur_saut_m = (g * t_vol**2) / 8
        hauteur_saut_cm = hauteur_saut_m * 100

        masse = poids_kg
        force_moyenne = masse * (g + (2 * hauteur_saut_m / t_vol ** 2))
        puissance = (force_moyenne * hauteur_saut_m) / t_vol

        st.success(f"Hauteur estimée : {hauteur_saut_cm:.1f} cm")
        st.info(f"Temps en vol : {t_vol:.3f} s")
        st.info(f"Force moyenne : {force_moyenne:.1f} N")
        st.info(f"Puissance moyenne : {puissance:.1f} W")

        # PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Rapport d'analyse de saut (Temps de vol)", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Date : {datetime.datetime.now().strftime('%d/%m/%Y')}", ln=True)
        pdf.cell(0, 10, f"Prénom : {prenom}", ln=True)
        pdf.cell(0, 10, f"Taille : {taille_cm} cm", ln=True)
        pdf.cell(0, 10, f"Poids : {poids_kg} kg", ln=True)
        pdf.cell(0, 10, f"Image décollage : {frame_decollage}", ln=True)
        pdf.cell(0, 10, f"Image atterrissage : {frame_atterrissage}", ln=True)
        pdf.cell(0, 10, f"Hauteur saut : {hauteur_saut_cm:.1f} cm", ln=True)
        pdf.cell(0, 10, f"Force : {force_moyenne:.1f} N", ln=True)
        pdf.cell(0, 10, f"Puissance : {puissance:.1f} W", ln=True)
        pdf_path = "rapport_saut.pdf"
        pdf.output(pdf_path)

        with open(pdf_path, "rb") as f:
            st.download_button("📄 Télécharger le rapport PDF", data=f, file_name=f"{prenom}_saut.pdf")

        os.remove(pdf_path)
        os.remove(video_path)
