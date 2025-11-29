import streamlit as st
import cv2
import time
import numpy as np
import physics
import camera
import os
from fpdf import FPDF

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Lumina: Spectral Triage", layout="wide")

# 2. PDF GENERATION ENGINE (ALIGNED)
def create_pdf(img_red, img_blood, img_surface, perfusion_score, status):
    """
    Generates a PDF report.
    FIX: Uses explicit Y-coordinates to align text perfectly next to images.
    """
    pdf = FPDF()
    pdf.add_page()
    
    # --- HEADER ---
    pdf.set_font('Helvetica', 'B', 20)
    pdf.cell(0, 10, 'Lumina Spectral Health Report', new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.set_font('Helvetica', 'I', 10)
    pdf.cell(0, 10, f'Generated on: {time.strftime("%Y-%m-%d %H:%M:%S")}', new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(10) # Add space before first section

    # --- SAVE TEMP IMAGES ---
    cv2.imwrite("temp_red.png", img_red)
    cv2.imwrite("temp_blood.png", img_blood)
    cv2.imwrite("temp_surface.png", img_surface)

    # --- HELPER TO PRINT SECTIONS ---
    def print_section(title, img_path, explanation):
        # 1. Print Title Bar
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 10, title, fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2) # Small gap
        
        # 2. Capture Top Y Position
        y_start = pdf.get_y()
        
        # 3. Place Image (Left Side) - Fixed Width 80, Aspect Ratio Auto
        pdf.image(img_path, x=10, y=y_start, w=80)
        
        # 4. Place Text (Right Side) - Align Top with Image
        pdf.set_xy(95, y_start) # Move cursor to X=95, Y=Top of Image
        pdf.set_font('Helvetica', '', 10)
        pdf.multi_cell(0, 5, explanation)
        
        # 5. Move Cursor Down for Next Section
        # We manually move down 65 units (Image height approx 60 + padding)
        pdf.set_y(y_start + 65)

    # --- SECTION 1: HEMOGLOBIN ---
    text_blood = (
        "WHAT THIS IS:\n"
        "This image shows where blood is pooling under your skin.\n\n"
        "HOW TO READ IT:\n"
        "- RED AREAS: High blood flow (oxygen-rich).\n"
        "- BLUE AREAS: Low blood flow.\n\n"
        "WHY IT MATTERS:\n"
        "Healthy skin looks red/orange. Large blue patches may indicate "
        "low circulation or pressure marks."
    )
    print_section('1. Hemoglobin Perfusion (Blood Flow)', "temp_blood.png", text_blood)

    # --- SECTION 2: SURFACE TEXTURE ---
    text_surface = (
        "WHAT THIS IS:\n"
        "Blue light stops at the surface, highlighting texture.\n\n"
        "HOW TO READ IT:\n"
        "This highlights roughness, dryness, and pigmentation (melanin). "
        "It acts like a microscope for skin texture.\n\n"
        "WHY IT MATTERS:\n"
        "Dark spots can reveal UV damage (sun spots) or Jaundice "
        "before they are visible to the naked eye."
    )
    print_section('2. Surface Texture & Pigment', "temp_surface.png", text_surface)

    # --- SECTION 3: DEEP TISSUE ---
    text_deep = (
        "WHAT THIS IS:\n"
        "Red light travels deep (up to 3mm) into your skin.\n\n"
        "HOW TO READ IT:\n"
        "Dark lines are veins. Since red light passes through skin, "
        "this ignores the surface and shows structure.\n\n"
        "MEDICAL NOTE:\n"
        "We use this as a 'Control' image to verify scan depth."
    )
    print_section('3. Deep Tissue Reference', "temp_red.png", text_deep)

    # --- FINAL SCORE ---
    pdf.ln(10) # Extra space at bottom
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, f'Calculated Perfusion Score: {perfusion_score:.1f} ({status})', new_x="LMARGIN", new_y="NEXT", align='C')

    return bytes(pdf.output())

# 3. CSS PLACEHOLDER
css_placeholder = st.empty()

def flash_screen(color_hex):
    css_placeholder.markdown(
        f"""
        <style>
        .stApp {{ background-color: {color_hex} !important; transition: background-color 0.2s; }}
        header {{visibility: hidden;}}
        </style>
        """,
        unsafe_allow_html=True
    )

# 4. CAMERA SETUP
@st.cache_resource
def get_camera():
    return camera.SpectralCamera(source=0)

try:
    cam = get_camera()
except Exception as e:
    st.error(f"Camera Error: {e}")
    st.stop()

# 5. UI LAYOUT
st.title("🩸 Lumina: Hyperspectral Triage")
st.markdown("**Instructions:** Maximize brightness. Press phone/laptop screen against skin. Click Start.")

status_text = st.empty()
btn_start = st.button("INITIATE SPECTRAL SCAN", type="primary")

# 6. SCAN LOGIC
if btn_start:
    # RED
    flash_screen("#FF0000")
    status_text.warning("ACQUIRING: RED CHANNEL (Deep Tissue)...")
    time.sleep(0.8) 
    frame_red = cam.get_frame()
    
    # GREEN
    flash_screen("#00FF00")
    status_text.warning("ACQUIRING: GREEN CHANNEL (Hemoglobin)...")
    time.sleep(0.8)
    frame_green = cam.get_frame()

    # BLUE
    flash_screen("#0000FF")
    status_text.warning("ACQUIRING: BLUE CHANNEL (Surface/Melanin)...")
    time.sleep(0.8)
    frame_blue = cam.get_frame()

    # RESET
    flash_screen("#0E1117") 
    status_text.success("Processing complete.")

    if frame_red is not None and frame_green is not None and frame_blue is not None:
        
        # MATH
        heatmap_blood = physics.calculate_hemoglobin(frame_red, frame_green)
        heatmap_surface = physics.calculate_surface_texture(frame_blue)
        perfusion_score = np.mean(heatmap_blood)
        
        # DIAGNOSIS LOGIC
        if perfusion_score < 80: status = "LOW / ISCHEMIC"
        elif perfusion_score > 180: status = "HIGH / INFLAMED"
        else: status = "NORMAL / HEALTHY"

        # DISPLAY
        st.divider()
        st.subheader(f"Analysis Result: {status}")
        
        c1, c2, c3 = st.columns(3)
        with c1: st.image(frame_red, channels="BGR", caption="Deep Tissue (Red Light)")
        with c2: st.image(heatmap_blood, caption="Hemoglobin Map (Blood Flow)")
        with c3: st.image(heatmap_surface, caption="Surface Texture (Blue Light)")

        # --- PDF DOWNLOAD BUTTON (THE NEW FEATURE) ---
        st.divider()
        st.markdown("### 📄 Patient Report")
        
        # Generate the PDF bytes
        pdf_bytes = create_pdf(frame_red, heatmap_blood, heatmap_surface, perfusion_score, status)
        
        st.download_button(
            label="Download Detailed PDF Report",
            data=pdf_bytes,
            file_name="Lumina_Report.pdf",
            mime="application/pdf"
        )
    
    else:
        st.error("Camera capture failed.")
