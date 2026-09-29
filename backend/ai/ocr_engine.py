import os
import io
import time
from typing import Dict, Any, List
from PIL import Image
import numpy as np

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

class LocalOCREngine:
    """
    On-device image and screenshot analysis engine.
    Runs 100% locally with zero cloud API dependencies.
    Performs layout detection, text region identification, image statistics,
    and text extraction.
    """
    def __init__(self):
        self.engine_name = "SnapAssist Local Vision & OCR Engine"

    def analyze_image(self, file_path: str) -> Dict[str, Any]:
        """
        Analyzes an image or screenshot locally.
        Returns:
            - text: extracted text / detected content
            - visual_type: UI screenshot, document, code, diagram/chart, photo
            - dimensions: {width, height}
            - text_regions_count: number of detected text/UI regions
            - visual_summary: human-readable summary
            - key_insights: list of notable findings
        """
        start_time = time.time()
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image not found at {file_path}")

        img = Image.open(file_path)
        width, height = img.size
        mode = img.mode

        # Convert to RGB numpy array
        rgb_img = img.convert("RGB")
        img_np = np.array(rgb_img)

        # Basic image statistics
        mean_brightness = float(np.mean(img_np))
        color_variance = float(np.var(img_np))

        # Layout & text region detection via OpenCV
        detected_boxes = []
        text_lines = []
        visual_type = "image"

        if HAS_CV2:
            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
            # Thresholding for edge & block detection
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            min_area = (width * height) * 0.0002
            max_area = (width * height) * 0.5
            
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if min_area < area < max_area:
                    x, y, w, h = cv2.boundingRect(cnt)
                    aspect = w / float(h)
                    # Text line regions typically have aspect ratio > 1.2 and height between 8 and 100
                    if 1.0 < aspect < 25.0 and 8 < h < 150:
                        detected_boxes.append({"x": int(x), "y": int(y), "w": int(w), "h": int(h)})

            # Classify visual type based on aspect ratio, color palette, and contour density
            if mean_brightness < 80 and len(detected_boxes) > 10:
                visual_type = "Dark Mode UI / IDE Screenshot"
            elif mean_brightness > 200 and len(detected_boxes) > 15:
                visual_type = "Document / Whitepaper Page"
            elif len(detected_boxes) > 20:
                visual_type = "Application Dashboard / System UI"
            elif color_variance > 3000:
                visual_type = "Graphic / Chart / Diagram"
            else:
                visual_type = "Photograph / General Image"

        # Check for optional tesseract OCR if installed locally
        extracted_text = ""
        try:
            import pytesseract
            extracted_text = pytesseract.image_to_string(img).strip()
        except Exception:
            pass

        # If tesseract is not installed on the system, generate a structured visual representation
        if not extracted_text:
            insights = [
                f"Image dimensions: {width}x{height} pixels ({mode} mode)",
                f"Classified visual content: {visual_type}",
                f"Detected UI/Text interactive blocks: {len(detected_boxes)} distinct regions",
                f"Mean image luminance: {mean_brightness:.1f}/255 ({'Dark Theme' if mean_brightness < 128 else 'Light Theme'})",
                f"Color complexity index: {color_variance:.1f}"
            ]
            extracted_text = f"[{visual_type}]\n" + "\n".join(f"• {item}" for item in insights)
        else:
            insights = [
                f"OCR text successfully extracted ({len(extracted_text.split())} words)",
                f"Classified visual layout: {visual_type}",
                f"Detected layout blocks: {len(detected_boxes)}"
            ]

        elapsed_ms = (time.time() - start_time) * 1000

        return {
            "text": extracted_text,
            "visual_type": visual_type,
            "dimensions": {"width": width, "height": height},
            "text_regions_count": len(detected_boxes),
            "mean_brightness": round(mean_brightness, 2),
            "elapsed_ms": round(elapsed_ms, 2),
            "insights": insights,
        }

_ocr_instance = None
def get_ocr_engine() -> LocalOCREngine:
    global _ocr_instance
    if _ocr_instance is None:
        _ocr_instance = LocalOCREngine()
    return _ocr_instance
