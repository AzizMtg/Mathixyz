import os
import cv2
import numpy as np
import requests
import base64
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from .latex_ocr import LaTeXOCR

load_dotenv()

class OCRService:
    def __init__(self):
        self.mathpix_app_id = os.getenv("MATHPIX_APP_ID")
        self.mathpix_app_key = os.getenv("MATHPIX_APP_KEY")
        self.use_mathpix = bool(self.mathpix_app_id and self.mathpix_app_key)
        self.latex_ocr = LaTeXOCR()
    
    async def extract_math(self, image_path: str) -> Dict[str, Any]:
        """Extract mathematical content from image"""
        
        # Preprocess image
        processed_image_path = await self._preprocess_image(image_path)
        
        # Try local LaTeX OCR first (more reliable)
        try:
            result = await self.latex_ocr.extract_latex(processed_image_path)
            return result
        except Exception as e:
            print(f"Local LaTeX OCR failed: {e}, trying Mathpix")
        
        # Fallback to Mathpix if available
        if self.use_mathpix:
            try:
                result = await self._mathpix_ocr(processed_image_path)
                return {
                    "latex": result.get("latex_styled", ""),
                    "confidence": result.get("latex_confidence", 0.0),
                    "text": result.get("text", ""),
                    "source": "mathpix"
                }
            except Exception as e:
                print(f"Mathpix OCR failed: {e}, falling back to mock")
        
        # Final fallback to mock LaTeX-OCR
        return await self._mock_latex_ocr(processed_image_path)
    
    async def _preprocess_image(self, image_path: str) -> str:
        """Preprocess image: deskew, denoise, enhance contrast"""
        
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Deskew
        coords = np.column_stack(np.where(gray > 0))
        if len(coords) > 0:
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            
            if abs(angle) > 0.5:  # Only rotate if significant skew
                (h, w) = gray.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                gray = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        # Save processed image
        processed_path = image_path.replace('.', '_processed.')
        cv2.imwrite(processed_path, enhanced)
        
        return processed_path
    
    async def _mathpix_ocr(self, image_path: str) -> Dict[str, Any]:
        """Use Mathpix API for OCR"""
        
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode()
        
        headers = {
            'app_id': self.mathpix_app_id,
            'app_key': self.mathpix_app_key,
            'Content-type': 'application/json'
        }
        
        data = {
            'src': f'data:image/jpeg;base64,{image_data}',
            'formats': ['latex_styled', 'text'],
            'data_options': {
                'include_latex': True,
                'include_mathml': False
            }
        }
        
        response = requests.post('https://api.mathpix.com/v3/text', 
                               headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        return response.json()
    
    async def _mock_latex_ocr(self, image_path: str) -> Dict[str, Any]:
        """Mock LaTeX-OCR for development (replace with actual LaTeX-OCR)"""
        
        # This would be replaced with actual LaTeX-OCR implementation
        # For now, return mock data based on filename patterns
        filename = os.path.basename(image_path).lower()
        
        if 'quadratic' in filename or 'equation' in filename:
            return {
                "latex": r"x^2 + 5x + 6 = 0",
                "confidence": 0.85,
                "text": "x squared plus 5x plus 6 equals 0",
                "source": "latex_ocr_mock"
            }
        elif 'integral' in filename or 'calculus' in filename:
            return {
                "latex": r"\int_{0}^{1} x^2 \, dx = \frac{1}{3}",
                "confidence": 0.90,
                "text": "integral from 0 to 1 of x squared dx equals one third",
                "source": "latex_ocr_mock"
            }
        elif 'fraction' in filename:
            return {
                "latex": r"\frac{3}{4} + \frac{1}{2} = \frac{5}{4}",
                "confidence": 0.88,
                "text": "three fourths plus one half equals five fourths",
                "source": "latex_ocr_mock"
            }
        else:
            # Generic math expression
            return {
                "latex": r"2x + 3 = 7",
                "confidence": 0.75,
                "text": "2x plus 3 equals 7",
                "source": "latex_ocr_mock"
            }
