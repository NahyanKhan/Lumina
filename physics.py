import cv2
import numpy as np

def calculate_hemoglobin(red_frame, green_frame):
    """
    Detects blood volume by subtracting Green absorption from Red reflection.
    Returns a colorized heatmap.
    """
    # 1. Convert to grayscale to get intensity
    r_gray = cv2.cvtColor(red_frame, cv2.COLOR_BGR2GRAY).astype(np.float32)
    g_gray = cv2.cvtColor(green_frame, cv2.COLOR_BGR2GRAY).astype(np.float32)

    # 2. The Physics Math: Subtraction
    # Where blood is present, Green is absorbed (darker), Red is reflected (lighter).
    # So (Red - Green) should be high in blood-rich areas.
    diff = r_gray - g_gray

    # 3. Normalize to 0-255 range for display
    diff = np.clip(diff, 0, 255)
    diff = cv2.normalize(diff, None, 0, 255, cv2.NORM_MINMAX)
    diff = diff.astype(np.uint8)

    # 4. Apply 'JET' colormap (Blue=Low Blood, Red=High Blood)
    heatmap = cv2.applyColorMap(diff, cv2.COLORMAP_JET)
    
    return heatmap

def calculate_surface_texture(blue_frame):
    """
    Blue light (460nm) doesn't penetrate deep. It shows surface texture/melanin.
    """
    b_gray = cv2.cvtColor(blue_frame, cv2.COLOR_BGR2GRAY)
    # Apply a high-contrast filter
    return cv2.applyColorMap(b_gray, cv2.COLORMAP_BONE)
