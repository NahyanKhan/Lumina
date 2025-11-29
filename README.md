# 🩸 Lumina: Hyperspectral Triage Prototype

### **Abstract**
Lumina is a Python-based research prototype that utilizes **Sequential Chromatic Illumination (SCI)** to perform non-invasive hemodynamic imaging using a standard smartphone/webcam. By using the screen as a programmable multi-spectral light source, the system isolates deep tissue structure (620nm), hemoglobin perfusion (530nm), and surface pigmentation (460nm).

### **Tech Stack**
- **Core Logic:** Python 3.9+
- **Computer Vision:** OpenCV (`cv2`)
- **Physics Engine:** NumPy (Beer-Lambert Law implementation)
- **Interface:** Streamlit
- **Reporting:** FPDF2

### **How to Run**
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```
4. Maximize screen brightness for optimal results.
5. Press the device screen against skin and click "INITIATE SPECTRAL SCAN".

### **Project Structure**
- `app.py` - Main Streamlit application
- `physics.py` - Hemoglobin detection and surface texture analysis
- `camera.py` - Webcam interface
- `requirements.txt` - Python dependencies

### **How It Works**
The system performs a three-phase spectral scan:
1. **Red Light (620nm)** - Deep tissue penetration for structural reference
2. **Green Light (530nm)** - Hemoglobin absorption measurement
3. **Blue Light (460nm)** - Surface texture and melanin detection

Using spectral subtraction (Red - Green channels), the system isolates pure hemoglobin distribution and calculates a Perfusion Index to assess blood flow.

### **Output**
- Real-time visual heatmaps (JET colormap)
- Quantitative Perfusion Index (0-255 scale)
- Clinical status classification (LOW/NORMAL/HIGH)
- Downloadable PDF report with layperson-friendly explanations

### **Disclaimer**
This is a research prototype for educational purposes only. Not intended for medical diagnosis.
