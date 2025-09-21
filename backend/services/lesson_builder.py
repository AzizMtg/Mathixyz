from typing import List, Dict, Any
from .ocr_service import OCRService
from .llm_service import LLMService
from .sympy_service import SymPyService

class LessonBuilder:
    def __init__(self, ocr_service: OCRService, llm_service: LLMService, sympy_service: SymPyService):
        self.ocr_service = ocr_service
        self.llm_service = llm_service
        self.sympy_service = sympy_service
    
    async def build_lesson(self, job_id: str, image_paths: List[str]) -> Dict[str, Any]:
        """Build structured lesson from processed images"""
        
        lesson_steps = []
        all_expressions = []
        
        # Process each image
        for i, image_path in enumerate(image_paths):
            # Extract mathematical content
            ocr_result = await self.ocr_service.extract_math(image_path)
            latex_expression = ocr_result["latex"]
            
            if not latex_expression:
                continue
            
            all_expressions.append(latex_expression)
            
            # Validate with SymPy
            validation_result = await self.sympy_service.validate_expression(latex_expression)
            
            # Generate explanation
            explanation = await self.llm_service.generate_explanation(
                latex_expression, 
                f"This is image {i+1} from a sequence of math problems"
            )
            
            # Build step data
            step_data = {
                "step_id": f"step_{i+1}",
                "image_index": i,
                "original_image": image_path,
                "ocr_result": ocr_result,
                "validation": validation_result,
                "explanation": explanation,
                "latex": latex_expression,
                "step_type": self._determine_step_type(latex_expression, explanation)
            }
            
            lesson_steps.append(step_data)
        
        # Generate lesson title
        lesson_title = self._generate_lesson_title(all_expressions, lesson_steps)
        
        # Add lesson summary
        lesson_summary = self._generate_lesson_summary(lesson_steps)
        
        return {
            "title": lesson_title,
            "summary": lesson_summary,
            "total_steps": len(lesson_steps),
            "steps": lesson_steps,
            "expressions_covered": all_expressions
        }
    
    def _determine_step_type(self, latex_expression: str, explanation: Dict[str, Any]) -> str:
        """Determine the type of mathematical step"""
        
        problem_type = explanation.get("problem_type", "").lower()
        
        if "quadratic" in problem_type:
            return "quadratic_equation"
        elif "integral" in problem_type or "integration" in problem_type:
            return "integration"
        elif "derivative" in problem_type or "differentiation" in problem_type:
            return "differentiation"
        elif "fraction" in problem_type:
            return "fraction_operations"
        elif "linear" in problem_type:
            return "linear_equation"
        elif "trigonometric" in problem_type:
            return "trigonometry"
        elif "logarithm" in problem_type:
            return "logarithms"
        else:
            return "general_algebra"
    
    def _generate_lesson_title(self, expressions: List[str], steps: List[Dict[str, Any]]) -> str:
        """Generate appropriate lesson title based on content"""
        
        if not steps:
            return "Math Problem Analysis"
        
        # Count step types
        step_types = [step["step_type"] for step in steps]
        type_counts = {}
        for step_type in step_types:
            type_counts[step_type] = type_counts.get(step_type, 0) + 1
        
        # Determine primary topic
        primary_type = max(type_counts, key=type_counts.get)
        
        title_map = {
            "quadratic_equation": "Solving Quadratic Equations",
            "integration": "Integration Problems",
            "differentiation": "Differentiation Problems", 
            "fraction_operations": "Working with Fractions",
            "linear_equation": "Linear Equations",
            "trigonometry": "Trigonometric Functions",
            "logarithms": "Logarithmic Functions",
            "general_algebra": "Algebraic Problem Solving"
        }
        
        base_title = title_map.get(primary_type, "Mathematical Problem Solving")
        
        if len(steps) > 1:
            return f"{base_title} - {len(steps)} Step Solution"
        else:
            return base_title
    
    def _generate_lesson_summary(self, steps: List[Dict[str, Any]]) -> str:
        """Generate lesson summary"""
        
        if not steps:
            return "No mathematical content found in the uploaded images."
        
        step_types = list(set(step["step_type"] for step in steps))
        
        summary = f"This lesson covers {len(steps)} mathematical problem(s) involving "
        
        type_descriptions = {
            "quadratic_equation": "quadratic equations",
            "integration": "integration techniques",
            "differentiation": "differentiation rules",
            "fraction_operations": "fraction arithmetic",
            "linear_equation": "linear equations",
            "trigonometry": "trigonometric functions",
            "logarithms": "logarithmic functions",
            "general_algebra": "algebraic manipulation"
        }
        
        descriptions = [type_descriptions.get(t, t.replace("_", " ")) for t in step_types]
        
        if len(descriptions) == 1:
            summary += descriptions[0]
        elif len(descriptions) == 2:
            summary += f"{descriptions[0]} and {descriptions[1]}"
        else:
            summary += f"{', '.join(descriptions[:-1])}, and {descriptions[-1]}"
        
        summary += ". Each step includes detailed explanations, key concepts, and common mistakes to avoid."
        
        return summary
