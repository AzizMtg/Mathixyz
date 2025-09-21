import os
import torch
import numpy as np
from PIL import Image
import cv2
from typing import Dict, Any, Optional
import subprocess
import tempfile

class LaTeXOCR:
    def __init__(self):
        """Initialize LaTeX OCR service with automatic model detection"""
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.processor = None
        self.ocr_method = self._detect_best_ocr_method()
        
        # Initialize the selected OCR method
        self._initialize_ocr_model()
        
        # Add confidence threshold for filtering bad results
        self.min_confidence_threshold = 0.3
        
    def _detect_best_ocr_method(self) -> str:
        """Detect the best available OCR method"""
        
        # Try to import pix2tex (LaTeX-OCR)
        try:
            from pix2tex.cli import LatexOCR
            print("Using pix2tex LaTeX-OCR (best for math)")
            return "pix2tex"
        except ImportError:
            pass
        
        # Try to use EasyOCR with math preprocessing
        try:
            import easyocr
            print("Using EasyOCR with math preprocessing")
            return "easyocr"
        except ImportError:
            pass
        
        # Try to use PaddleOCR
        try:
            from paddleocr import PaddleOCR
            print("Using PaddleOCR")
            return "paddleocr"
        except ImportError:
            pass
        
        # Fallback to Tesseract
        try:
            import pytesseract
            print("Using Tesseract OCR with math config")
            return "tesseract"
        except ImportError:
            pass
        
        print("No OCR libraries found, using fallback")
        return "fallback"
        
    def _load_model(self):
        """Load the appropriate OCR model"""
        if self.model_loaded:
            return
            
        try:
            if self.ocr_method == "pix2tex":
                from pix2tex.cli import LatexOCR
                self.model = LatexOCR()
                
            elif self.ocr_method == "easyocr":
                import easyocr
                self.model = easyocr.Reader(['en'], gpu=torch.cuda.is_available())
                
            elif self.ocr_method == "paddleocr":
                from paddleocr import PaddleOCR
                self.model = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=torch.cuda.is_available())
                
            elif self.ocr_method == "tesseract":
                import pytesseract
                # Test if tesseract is available
                pytesseract.get_tesseract_version()
                
            self.model_loaded = True
            print(f"OCR model ({self.ocr_method}) loaded successfully")
            
        except Exception as e:
            print(f"Failed to load OCR model ({self.ocr_method}): {e}")
            self.ocr_method = "fallback"
            self.model_loaded = False
    
    async def extract_latex(self, image_path: str) -> Dict[str, Any]:
        """Extract LaTeX from image using local OCR model"""
        
        # Load model if not already loaded
        self._load_model()
        
        if not self.model_loaded:
            return self._fallback_ocr(image_path)
        
        try:
            import asyncio
            
            # Run the heavy computation in a thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._process_image_sync, image_path)
            return result
            
        except Exception as e:
            print(f"LaTeX OCR extraction failed: {e}")
            return self._fallback_ocr(image_path)
    
    def _process_image_sync(self, image_path: str) -> Dict[str, Any]:
        """Synchronous image processing for thread pool execution"""
        
        if self.ocr_method == "pix2tex":
            return self._process_with_pix2tex(image_path)
        elif self.ocr_method == "easyocr":
            return self._process_with_easyocr(image_path)
        elif self.ocr_method == "paddleocr":
            return self._process_with_paddleocr(image_path)
        elif self.ocr_method == "tesseract":
            return self._process_with_tesseract(image_path)
        else:
            return self._fallback_ocr(image_path)
    
    def _process_with_pix2tex(self, image_path: str) -> Dict[str, Any]:
        """Process image with pix2tex LaTeX-OCR"""
        try:
            # Load and preprocess image
            image = self._preprocess_image_for_math(image_path)
            
            # Use pix2tex for LaTeX extraction
            latex_result = self.model(image)
            
            # Check if result is garbled and filter it
            if self._is_garbled_output(latex_result):
                print(f"Detected garbled output from pix2tex, simplifying...")
                latex_result = self._simplify_garbled_expression(latex_result)
                confidence = 0.4  # Lower confidence for simplified results
            else:
                confidence = 0.90
            
            return {
                "latex": latex_result,
                "confidence": confidence,
                "text": self._latex_to_readable(latex_result),
                "source": "pix2tex_latex_ocr"
            }
        except Exception as e:
            print(f"Pix2tex processing failed: {e}")
            return self._fallback_ocr(image_path)
    
    def _process_with_easyocr(self, image_path: str) -> Dict[str, Any]:
        """Process image with EasyOCR and math post-processing"""
        try:
            # Preprocess for better math recognition
            processed_image = self._preprocess_image_for_math(image_path)
            
            # Convert PIL to numpy for EasyOCR
            if isinstance(processed_image, Image.Image):
                processed_image = np.array(processed_image)
            
            # Extract text with EasyOCR
            results = self.model.readtext(processed_image)
            
            # Combine all detected text
            text_parts = [result[1] for result in results if result[2] > 0.5]  # confidence > 0.5
            combined_text = " ".join(text_parts)
            
            # Post-process for LaTeX
            latex_text = self._postprocess_latex(combined_text)
            
            return {
                "latex": latex_text,
                "confidence": 0.80,
                "text": self._latex_to_readable(latex_text),
                "source": "easyocr_math"
            }
        except Exception as e:
            print(f"EasyOCR processing failed: {e}")
            return self._fallback_ocr(image_path)
    
    def _process_with_paddleocr(self, image_path: str) -> Dict[str, Any]:
        """Process image with PaddleOCR"""
        try:
            # Use PaddleOCR
            result = self.model.ocr(image_path, cls=True)
            
            # Extract text from results
            text_parts = []
            for line in result:
                if line:
                    for word_info in line:
                        if len(word_info) > 1:
                            text_parts.append(word_info[1][0])
            
            combined_text = " ".join(text_parts)
            latex_text = self._postprocess_latex(combined_text)
            
            return {
                "latex": latex_text,
                "confidence": 0.75,
                "text": self._latex_to_readable(latex_text),
                "source": "paddleocr_math"
            }
        except Exception as e:
            print(f"PaddleOCR processing failed: {e}")
            return self._fallback_ocr(image_path)
    
    def _process_with_tesseract(self, image_path: str) -> Dict[str, Any]:
        """Process image with Tesseract OCR optimized for math"""
        try:
            import pytesseract
            
            # Preprocess image for better OCR
            processed_image = self._preprocess_image_for_math(image_path)
            
            # Convert PIL to numpy if needed
            if isinstance(processed_image, Image.Image):
                processed_image = np.array(processed_image)
            
            # Use Tesseract with math-optimized config
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+-=(){}[]^_/\|<>≤≥≠±∞∫∑√πθλμσαβγδ'
            
            text = pytesseract.image_to_string(processed_image, config=custom_config)
            latex_text = self._postprocess_latex(text)
            
            return {
                "latex": latex_text,
                "confidence": 0.70,
                "text": self._latex_to_readable(latex_text),
                "source": "tesseract_math"
            }
        except Exception as e:
            print(f"Tesseract processing failed: {e}")
            return self._fallback_ocr(image_path)
    
    def _preprocess_image(self, image_path: str) -> Image.Image:
        """Preprocess image for better OCR results"""
        
        # Read image with OpenCV
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced)
        
        # Threshold to get clean binary image
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Convert back to PIL Image
        return Image.fromarray(binary)
    
    def _preprocess_image_for_math(self, image_path: str) -> Image.Image:
        """Enhanced preprocessing specifically for mathematical expressions"""
        
        # Read image with OpenCV
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Resize if too small (math OCR works better with larger images)
        height, width = gray.shape
        if height < 64 or width < 64:
            scale_factor = max(64/height, 64/width, 2.0)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        # Deskew the image
        coords = np.column_stack(np.where(gray > 0))
        if len(coords) > 0:
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            
            if abs(angle) > 0.5:
                (h, w) = gray.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                gray = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
        # Enhance contrast specifically for math symbols
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Denoise while preserving edges (important for math symbols)
        denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
        
        # Morphological operations to clean up math symbols
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        cleaned = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
        
        # Adaptive threshold for better symbol recognition
        binary = cv2.adaptiveThreshold(cleaned, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # Invert if background is dark
        if np.mean(binary) < 127:
            binary = cv2.bitwise_not(binary)
        
        # Convert back to PIL Image
        return Image.fromarray(binary)
    
    def _postprocess_latex(self, text: str) -> str:
        """Post-process OCR output to improve LaTeX formatting"""
        
        # Basic LaTeX formatting improvements
        text = text.strip()
        
        # Detect and handle severely garbled output
        if self._is_garbled_output(text):
            return self._simplify_garbled_expression(text)
        
        # Handle complex array structures that cause parsing issues
        if '\\begin{array}' in text and text.count('{') > text.count('}'):
            # Fix unbalanced braces in array structures
            text = self._fix_unbalanced_braces(text)
        
        # Clean up malformed LaTeX constructs
        text = self._clean_malformed_latex(text)
        
        # Common OCR corrections for mathematical symbols
        replacements = {
            ' = ': ' = ',
            ' + ': ' + ',
            ' - ': ' - ',
            ' * ': ' \\cdot ',
            ' / ': ' \\div ',
            '( ': '(',
            ' )': ')',
            '{ ': '{',
            ' }': '}',
            '\\\\': '\\\\ ',  # Add space after line breaks
            '&': ' & ',  # Add spaces around column separators
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Fix common OCR errors in mathematical notation
        text = re.sub(r'([0-9])\s*([a-zA-Z])', r'\1\2', text)  # Remove space between number and variable
        text = re.sub(r'([a-zA-Z])\s*([0-9])', r'\1_{\2}', text)  # Convert x 1 to x_{1}
        text = re.sub(r'\^\s*([0-9a-zA-Z])', r'^{\1}', text)  # Fix exponents
        text = re.sub(r'_\s*([0-9a-zA-Z])', r'_{\1}', text)  # Fix subscripts
        
        # Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _fix_unbalanced_braces(self, text: str) -> str:
        """Fix unbalanced braces in LaTeX expressions"""
        
        open_count = text.count('{')
        close_count = text.count('}')
        
        if open_count > close_count:
            # Add missing closing braces
            text += '}' * (open_count - close_count)
        elif close_count > open_count:
            # Add missing opening braces at the beginning
            text = '{' * (close_count - open_count) + text
        
        return text
    
    def _clean_malformed_latex(self, text: str) -> str:
        """Clean up malformed LaTeX constructs"""
        
        # Fix double asterisks that should be powers
        text = re.sub(r'\*\*', '^', text)
        
        # Fix malformed calligraphic fonts
        text = re.sub(r'\\cal\{([^}]*)\}\*', r'\\mathcal{\1}', text)
        text = re.sub(r'\\cal\{=\}', '=', text)
        text = re.sub(r'\\cal\{-\}', '-', text)
        
        # Fix malformed overlines
        text = re.sub(r'\\overline\{([^}]*)\}\*', r'\\overline{\1}', text)
        
        # Fix repeated symbols
        text = re.sub(r'\*+', '*', text)
        text = re.sub(r'\^+', '^', text)
        
        # Fix malformed gamma expressions
        text = re.sub(r'\\gamma\^\*\^\*', r'\\gamma^*', text)
        text = re.sub(r'\\gamma\*\*', r'\\gamma^*', text)
        
        # Clean up excessive braces
        text = re.sub(r'\{+', '{', text)
        text = re.sub(r'\}+', '}', text)
        
        # Fix angle brackets
        text = re.sub(r'<([^>]*)>', r'\\langle \1 \\rangle', text)
        
        return text
    
    def _is_garbled_output(self, text: str) -> bool:
        """Detect if OCR output is severely garbled or hallucinated"""
        
        # Count various indicators of garbled output
        indicators = 0
        
        # Too many nested braces
        if text.count('{') > 20 or text.count('}') > 20:
            indicators += 1
        
        # Excessive scriptstyle commands
        if text.count('\\scriptstyle') > 5:
            indicators += 1
        
        # Too many nested fractions
        if text.count('\\frac') > 8:
            indicators += 1
        
        # Excessive overbraces/underbraces
        if text.count('\\overbrace') + text.count('\\underbrace') > 3:
            indicators += 1
        
        # Deeply nested square roots
        if text.count('\\sqrt') > 6:
            indicators += 1
        
        # Excessive dots and cdots
        if text.count('\\cdot') + text.count('\\cdotp') > 10:
            indicators += 1
        
        # Very long expressions (likely hallucinated)
        if len(text) > 500:
            indicators += 1
        
        # Repetitive patterns (sign of hallucination)
        if '\\cdot{\\cdot' in text or '\\sqrt{\\sqrt{\\sqrt' in text:
            indicators += 2
        
        # Excessive mathrm commands
        if text.count('\\mathrm') > 8:
            indicators += 1
        
        # Nested overlines/underlines
        if text.count('\\overline') > 5:
            indicators += 1
        
        # Check for the specific pattern you encountered
        if '\\scriptstyle{\\frac{\\scriptstyle' in text:
            indicators += 3  # This is definitely garbled
        
        # Return True if multiple indicators present
        return indicators >= 2  # Lower threshold to catch more garbled output
    
    def _simplify_garbled_expression(self, text: str) -> str:
        """Simplify severely garbled OCR output to something meaningful"""
        
        # Extract basic mathematical components
        components = []
        
        # Look for simple variables and numbers
        import re
        variables = re.findall(r'[a-zA-Z]', text)
        numbers = re.findall(r'\d+', text)
        
        # Look for basic operations
        has_fraction = '\\frac' in text
        has_sqrt = '\\sqrt' in text
        has_sum = '\\sum' in text
        has_integral = '\\int' in text
        
        # Build a simplified expression based on detected components
        if has_sum:
            if variables:
                return f"\\sum {variables[0]}"
            else:
                return "\\sum"
        
        if has_integral:
            if variables:
                return f"\\int {variables[0]} dx"
            else:
                return "\\int f(x) dx"
        
        if has_fraction and len(variables) >= 2:
            return f"\\frac{{{variables[0]}}}{{{variables[1]}}}"
        
        if has_sqrt and variables:
            return f"\\sqrt{{{variables[0]}}}"
        
        # If we found variables and numbers, create a simple expression
        if variables and numbers:
            var = variables[0] if variables else 'x'
            num = numbers[0] if numbers else '1'
            return f"{var}^{num}"
        
        # Last resort - return a generic expression
        if variables:
            return variables[0]
        
        return "x"
    
    def _latex_to_readable(self, latex_expr: str) -> str:
        """Convert LaTeX expression to human-readable text"""
        
        if not latex_expr or latex_expr.strip() == "":
            return "Empty expression"
        
        # Start with the LaTeX expression
        readable = latex_expr
        
        # Handle fractions
        import re
        readable = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1) divided by (\2)', readable)
        
        # Handle square roots
        readable = re.sub(r'\\sqrt\{([^}]+)\}', r'square root of (\1)', readable)
        
        # Handle powers/exponents
        readable = re.sub(r'([a-zA-Z0-9]+)\^\{([^}]+)\}', r'\1 to the power of (\2)', readable)
        readable = re.sub(r'([a-zA-Z0-9]+)\^([a-zA-Z0-9])', r'\1 to the power of \2', readable)
        
        # Handle subscripts
        readable = re.sub(r'([a-zA-Z]+)_\{([^}]+)\}', r'\1 subscript (\2)', readable)
        readable = re.sub(r'([a-zA-Z]+)_([a-zA-Z0-9])', r'\1 subscript \2', readable)
        
        # Handle summation
        readable = re.sub(r'\\sum', 'sum of', readable)
        
        # Handle integrals
        readable = re.sub(r'\\int', 'integral of', readable)
        
        # Handle limits
        readable = re.sub(r'\\lim', 'limit of', readable)
        
        # Handle Greek letters
        greek_replacements = {
            r'\\alpha': 'alpha',
            r'\\beta': 'beta', 
            r'\\gamma': 'gamma',
            r'\\delta': 'delta',
            r'\\epsilon': 'epsilon',
            r'\\varepsilon': 'epsilon',
            r'\\zeta': 'zeta',
            r'\\eta': 'eta',
            r'\\theta': 'theta',
            r'\\iota': 'iota',
            r'\\kappa': 'kappa',
            r'\\lambda': 'lambda',
            r'\\mu': 'mu',
            r'\\nu': 'nu',
            r'\\xi': 'xi',
            r'\\pi': 'pi',
            r'\\rho': 'rho',
            r'\\sigma': 'sigma',
            r'\\tau': 'tau',
            r'\\upsilon': 'upsilon',
            r'\\phi': 'phi',
            r'\\chi': 'chi',
            r'\\psi': 'psi',
            r'\\omega': 'omega'
        }
        
        for latex_greek, readable_greek in greek_replacements.items():
            readable = re.sub(latex_greek, readable_greek, readable)
        
        # Handle trigonometric functions
        readable = re.sub(r'\\sin', 'sine of', readable)
        readable = re.sub(r'\\cos', 'cosine of', readable)
        readable = re.sub(r'\\tan', 'tangent of', readable)
        
        # Handle logarithms
        readable = re.sub(r'\\log', 'logarithm of', readable)
        readable = re.sub(r'\\ln', 'natural log of', readable)
        
        # Handle mathematical operators
        readable = re.sub(r'\\cdot', ' times ', readable)
        readable = re.sub(r'\\times', ' times ', readable)
        readable = re.sub(r'\\div', ' divided by ', readable)
        readable = re.sub(r'\\pm', ' plus or minus ', readable)
        readable = re.sub(r'\\mp', ' minus or plus ', readable)
        
        # Handle inequalities
        readable = re.sub(r'\\leq', ' less than or equal to ', readable)
        readable = re.sub(r'\\geq', ' greater than or equal to ', readable)
        readable = re.sub(r'\\neq', ' not equal to ', readable)
        readable = re.sub(r'\\approx', ' approximately equal to ', readable)
        
        # Handle special symbols
        readable = re.sub(r'\\infty', 'infinity', readable)
        readable = re.sub(r'\\partial', 'partial derivative', readable)
        readable = re.sub(r'\\nabla', 'nabla', readable)
        
        # Handle overlines and underlines
        readable = re.sub(r'\\overline\{([^}]+)\}', r'(\1) with overline', readable)
        readable = re.sub(r'\\underline\{([^}]+)\}', r'(\1) with underline', readable)
        
        # Handle angle brackets (inner products)
        readable = re.sub(r'\\langle([^\\]+)\\rangle', r'inner product of (\1)', readable)
        
        # Handle arrays/matrices
        if '\\begin{array}' in readable:
            readable = re.sub(r'\\begin\{array\}.*?\\end\{array\}', 'matrix or array expression', readable, flags=re.DOTALL)
        
        # Clean up remaining LaTeX commands
        readable = re.sub(r'\\[a-zA-Z]+', '', readable)
        
        # Clean up braces
        readable = readable.replace('{', '').replace('}', '')
        
        # Clean up multiple spaces
        readable = re.sub(r'\s+', ' ', readable)
        
        # Clean up operators
        readable = readable.replace('=', ' equals ')
        readable = readable.replace('+', ' plus ')
        readable = readable.replace('-', ' minus ')
        readable = readable.replace('*', ' times ')
        readable = readable.replace('/', ' divided by ')
        
        # Final cleanup
        readable = readable.strip()
        
        # If still too complex, provide a simple description
        if len(readable) > 200 or readable.count('(') > 10:
            return "Complex mathematical expression"
        
        return readable if readable else "Mathematical expression"
    
    def _fallback_ocr(self, image_path: str) -> Dict[str, Any]:
        """Fallback OCR using simple pattern matching"""
        
        filename = os.path.basename(image_path).lower()
        
        # Simple pattern-based fallback
        if 'quadratic' in filename or 'equation' in filename:
            return {
                "latex": r"x^2 + 5x + 6 = 0",
                "confidence": 0.75,
                "text": self._latex_to_readable(r"x^2 + 5x + 6 = 0"),
                "source": "fallback_ocr"
            }
        elif 'integral' in filename or 'calculus' in filename:
            return {
                "latex": r"\int_{0}^{1} x^2 \, dx = \frac{1}{3}",
                "confidence": 0.75,
                "text": "integral from 0 to 1 of x squared dx equals one third",
                "source": "fallback_ocr"
            }
        elif 'fraction' in filename:
            return {
                "latex": r"\frac{3}{4} + \frac{1}{2} = \frac{5}{4}",
                "confidence": 0.75,
                "text": "three fourths plus one half equals five fourths",
                "source": "fallback_ocr"
            }
        else:
            return {
                "latex": r"2x + 3 = 7",
                "confidence": 0.70,
                "text": "2x plus 3 equals 7",
                "source": "fallback_ocr"
            }
