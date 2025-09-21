import os
import json
from typing import Dict, Any, List
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.use_openrouter = bool(self.api_key)
        if self.use_openrouter:
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key
            )
    
    async def generate_explanation(self, latex_expression: str, context: str = "") -> Dict[str, Any]:
        """Generate step-by-step explanation for mathematical expression"""
        
        if self.use_openrouter:
            try:
                return await self._nemotron_explanation(latex_expression, context)
            except Exception as e:
                print(f"Nemotron API failed: {e}, falling back to mock")
        
        # Fallback to mock explanations
        return await self._mock_explanation(latex_expression, context)
    
    async def _nemotron_explanation(self, latex_expression: str, context: str = "") -> Dict[str, Any]:
        """Use Nemotron via OpenRouter for explanation generation"""
        
        prompt = f"""
        You are a math tutor. Given the following mathematical expression in LaTeX format, provide a clear, step-by-step explanation.
        
        Expression: {latex_expression}
        Context: {context}
        
        Please provide:
        1. A brief description of what type of problem this is
        2. Step-by-step solution with explanations
        3. Key concepts involved
        4. Common mistakes to avoid
        
        Format your response as JSON with the following structure:
        {{
            "problem_type": "description of problem type",
            "steps": [
                {{
                    "step_number": 1,
                    "description": "what we're doing in this step",
                    "latex": "mathematical expression for this step",
                    "explanation": "why we do this step"
                }}
            ],
            "key_concepts": ["concept1", "concept2"],
            "common_mistakes": ["mistake1", "mistake2"],
            "final_answer": "final result in LaTeX"
        }}
        """
        
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            completion = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    extra_headers={
                        "HTTP-Referer": "https://mathscrap.local",
                        "X-Title": "Math Scrap to Lesson App",
                    },
                    model="nvidia/nemotron-nano-9b-v2:free",
                    messages=[
                        {"role": "system", "content": "You are a helpful math tutor that explains mathematical concepts clearly. Always respond with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1500
                )
            )
            
            content = completion.choices[0].message.content.strip()
            
            # Clean content and try to parse JSON
            if content.startswith('```json'):
                content = content[7:-3].strip()
            elif content.startswith('```'):
                content = content[3:-3].strip()
            
            try:
                explanation = json.loads(content)
            except json.JSONDecodeError:
                # If JSON parsing fails, create a structured response
                explanation = {
                    "problem_type": "Mathematical Expression",
                    "steps": [
                        {
                            "step_number": 1,
                            "description": "Analyze the expression",
                            "latex": latex_expression,
                            "explanation": content
                        }
                    ],
                    "key_concepts": ["Mathematical Analysis"],
                    "common_mistakes": ["Parsing errors"],
                    "final_answer": latex_expression
                }
            
            explanation["source"] = "nemotron_openrouter"
            return explanation
            
        except Exception as e:
            print(f"Nemotron API error: {e}")
            raise
    
    async def _mock_explanation(self, latex_expression: str, context: str = "") -> Dict[str, Any]:
        """Generate mock explanations for development"""
        
        # Simple pattern matching for common math expressions
        expr_lower = latex_expression.lower()
        
        if "x^2" in latex_expression and "=" in latex_expression:
            return {
                "problem_type": "Quadratic Equation",
                "steps": [
                    {
                        "step_number": 1,
                        "description": "Identify the quadratic equation in standard form",
                        "latex": latex_expression,
                        "explanation": "This is a quadratic equation of the form ax² + bx + c = 0"
                    },
                    {
                        "step_number": 2,
                        "description": "Apply the quadratic formula or factoring",
                        "latex": r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}",
                        "explanation": "We can use the quadratic formula to find the solutions"
                    },
                    {
                        "step_number": 3,
                        "description": "Calculate the discriminant",
                        "latex": r"\Delta = b^2 - 4ac",
                        "explanation": "The discriminant tells us about the nature of the roots"
                    }
                ],
                "key_concepts": ["Quadratic Formula", "Discriminant", "Factoring"],
                "common_mistakes": ["Forgetting the ± sign", "Arithmetic errors in calculation"],
                "final_answer": r"x = -2, x = -3",
                "source": "mock_llm"
            }
        
        elif "\\int" in latex_expression:
            return {
                "problem_type": "Definite Integral",
                "steps": [
                    {
                        "step_number": 1,
                        "description": "Identify the function to integrate",
                        "latex": latex_expression,
                        "explanation": "We need to find the antiderivative of the given function"
                    },
                    {
                        "step_number": 2,
                        "description": "Apply the power rule",
                        "latex": r"\int x^n \, dx = \frac{x^{n+1}}{n+1} + C",
                        "explanation": "For polynomial functions, we use the power rule"
                    },
                    {
                        "step_number": 3,
                        "description": "Evaluate at the bounds",
                        "latex": r"F(b) - F(a)",
                        "explanation": "Apply the fundamental theorem of calculus"
                    }
                ],
                "key_concepts": ["Integration", "Power Rule", "Fundamental Theorem of Calculus"],
                "common_mistakes": ["Forgetting to add 1 to the exponent", "Sign errors"],
                "final_answer": r"\frac{1}{3}",
                "source": "mock_llm"
            }
        
        elif "\\frac" in latex_expression:
            return {
                "problem_type": "Fraction Operations",
                "steps": [
                    {
                        "step_number": 1,
                        "description": "Identify the fractions to add",
                        "latex": latex_expression,
                        "explanation": "We need to add fractions with different denominators"
                    },
                    {
                        "step_number": 2,
                        "description": "Find common denominator",
                        "latex": r"\text{LCD} = 4",
                        "explanation": "The least common denominator is 4"
                    },
                    {
                        "step_number": 3,
                        "description": "Convert and add",
                        "latex": r"\frac{3}{4} + \frac{2}{4} = \frac{5}{4}",
                        "explanation": "Convert to equivalent fractions and add numerators"
                    }
                ],
                "key_concepts": ["Common Denominators", "Equivalent Fractions", "Addition of Fractions"],
                "common_mistakes": ["Adding denominators", "Not simplifying the result"],
                "final_answer": r"\frac{5}{4}",
                "source": "mock_llm"
            }
        
        else:
            return {
                "problem_type": "Linear Equation",
                "steps": [
                    {
                        "step_number": 1,
                        "description": "Isolate the variable term",
                        "latex": latex_expression,
                        "explanation": "We want to get x by itself on one side"
                    },
                    {
                        "step_number": 2,
                        "description": "Subtract 3 from both sides",
                        "latex": r"2x = 7 - 3",
                        "explanation": "This eliminates the constant term on the left side"
                    },
                    {
                        "step_number": 3,
                        "description": "Divide by coefficient of x",
                        "latex": r"x = \frac{4}{2} = 2",
                        "explanation": "Divide both sides by 2 to solve for x"
                    }
                ],
                "key_concepts": ["Linear Equations", "Inverse Operations", "Algebraic Manipulation"],
                "common_mistakes": ["Sign errors", "Not applying operations to both sides"],
                "final_answer": r"x = 2",
                "source": "mock_llm"
            }
