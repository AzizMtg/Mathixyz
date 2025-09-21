import sympy as sp
from typing import Dict, Any, List, Optional
import re

class SymPyService:
    def __init__(self):
        # Define common symbols
        self.x, self.y, self.z = sp.symbols('x y z')
        self.t = sp.symbols('t')
    
    async def validate_expression(self, latex_expression: str) -> Dict[str, Any]:
        """Validate and analyze mathematical expression using SymPy"""
        
        try:
            # Convert LaTeX to SymPy expression
            sympy_expr = self._latex_to_sympy(latex_expression)
            
            if sympy_expr is None:
                return {
                    "valid": False,
                    "error": "Could not parse LaTeX expression",
                    "original_latex": latex_expression
                }
            
            # Analyze the expression
            analysis = await self._analyze_expression(sympy_expr, latex_expression)
            
            return {
                "valid": True,
                "sympy_expression": str(sympy_expr),
                "simplified": str(sp.simplify(sympy_expr)),
                "analysis": analysis,
                "original_latex": latex_expression
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "original_latex": latex_expression
            }
    
    async def solve_equation(self, latex_equation: str) -> Dict[str, Any]:
        """Solve mathematical equation using SymPy"""
        
        try:
            # Parse equation (split on =)
            if '=' not in latex_equation:
                return {
                    "solvable": False,
                    "error": "No equation found (missing = sign)",
                    "original_latex": latex_equation
                }
            
            left_side, right_side = latex_equation.split('=', 1)
            left_expr = self._latex_to_sympy(left_side.strip())
            right_expr = self._latex_to_sympy(right_side.strip())
            
            if left_expr is None or right_expr is None:
                return {
                    "solvable": False,
                    "error": "Could not parse equation sides",
                    "original_latex": latex_equation
                }
            
            # Create equation
            equation = sp.Eq(left_expr, right_expr)
            
            # Find variables to solve for
            variables = list(equation.free_symbols)
            
            if not variables:
                return {
                    "solvable": False,
                    "error": "No variables found in equation",
                    "original_latex": latex_equation
                }
            
            # Solve for each variable
            solutions = {}
            for var in variables:
                try:
                    sol = sp.solve(equation, var)
                    solutions[str(var)] = [str(s) for s in sol]
                except:
                    solutions[str(var)] = "Could not solve"
            
            return {
                "solvable": True,
                "equation": str(equation),
                "variables": [str(v) for v in variables],
                "solutions": solutions,
                "original_latex": latex_equation
            }
            
        except Exception as e:
            return {
                "solvable": False,
                "error": str(e),
                "original_latex": latex_equation
            }
    
    def _latex_to_sympy(self, latex_expr: str) -> Optional[sp.Expr]:
        """Convert LaTeX expression to SymPy expression with enhanced error handling"""
        
        try:
            # Clean up the LaTeX
            expr = latex_expr.strip()
            
            # Handle complex array structures - extract meaningful content
            if '\\begin{array}' in expr:
                return self._handle_array_expression(expr)
            
            # Handle overline notation
            expr = re.sub(r'\\overline\{([^}]+)\}', r'\1', expr)
            
            # Handle calligraphic fonts
            expr = re.sub(r'\\cal\{([^}]+)\}', r'\1', expr)
            
            # Handle angle brackets (inner products)
            expr = re.sub(r'\\langle([^\\]+)\\rangle', r'(\1)', expr)
            
            # Handle common LaTeX patterns
            # Fractions: \frac{a}{b} -> a/b
            expr = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1)/(\2)', expr)
            
            # Powers: x^{n} -> x**n, x^n -> x**n
            expr = re.sub(r'\^\{([^}]+)\}', r'**(\1)', expr)
            expr = re.sub(r'\^([a-zA-Z0-9])', r'**\1', expr)
            
            # Square roots: \sqrt{x} -> sqrt(x)
            expr = re.sub(r'\\sqrt\{([^}]+)\}', r'sqrt(\1)', expr)
            
            # Subscripts: x_{n} -> x_n (keep for variable names)
            expr = re.sub(r'_\{([^}]+)\}', r'_\1', expr)
            
            # Greek letters - convert to English equivalents
            greek_map = {
                r'\\gamma': 'gamma', r'\\alpha': 'alpha', r'\\beta': 'beta',
                r'\\delta': 'delta', r'\\epsilon': 'epsilon', r'\\varepsilon': 'epsilon',
                r'\\lambda': 'lambda', r'\\mu': 'mu', r'\\nu': 'nu',
                r'\\pi': 'pi', r'\\theta': 'theta', r'\\sigma': 'sigma'
            }
            for latex_greek, english in greek_map.items():
                expr = re.sub(latex_greek, english, expr)
            
            # Integrals: \int -> (remove for now, handle separately)
            expr = re.sub(r'\\int(_\{[^}]+\})?\^?\{?[^}]*\}?', '', expr)
            expr = re.sub(r'\\,?\s*dx?', '', expr)
            
            # Trigonometric functions
            expr = re.sub(r'\\sin', 'sin', expr)
            expr = re.sub(r'\\cos', 'cos', expr)
            expr = re.sub(r'\\tan', 'tan', expr)
            
            # Logarithms
            expr = re.sub(r'\\log', 'log', expr)
            expr = re.sub(r'\\ln', 'ln', expr)
            
            # Sum notation
            expr = re.sub(r'\\sum(_\{[^}]+\})?\^?\{?[^}]*\}?', 'sum', expr)
            
            # Remove remaining LaTeX commands
            expr = re.sub(r'\\[a-zA-Z]+', '', expr)
            
            # Clean up spaces and formatting
            expr = expr.replace(' ', '')
            expr = expr.replace('{', '(').replace('}', ')')
            
            # Handle special characters that might cause issues
            expr = re.sub(r'[^\w\d\+\-\*\/\(\)\.\=\,\_]', '', expr)
            
            # If expression is too complex or empty, return a simple placeholder
            if len(expr) < 2 or len(expr) > 200:
                return sp.Symbol('complex_expression')
            
            # Parse with SymPy
            return sp.sympify(expr)
            
        except Exception as e:
            # Return a symbolic representation for complex expressions
            print(f"LaTeX parsing failed: {e}")
            return sp.Symbol('unparseable_expression')
    
    def _handle_array_expression(self, latex_expr: str) -> sp.Expr:
        """Handle LaTeX array expressions by extracting meaningful mathematical content"""
        
        try:
            # Extract content between array delimiters
            array_content = re.search(r'\\begin\{array\}.*?\\end\{array\}', latex_expr, re.DOTALL)
            if not array_content:
                return sp.Symbol('array_expression')
            
            content = array_content.group(0)
            
            # Remove array structure commands
            content = re.sub(r'\\begin\{array\}\{[^}]*\}', '', content)
            content = re.sub(r'\\end\{array\}', '', content)
            
            # Split by row separators and extract meaningful expressions
            rows = content.split('\\\\')
            expressions = []
            
            for row in rows:
                # Split by column separators
                cells = re.split(r'&', row)
                for cell in cells:
                    cell = cell.strip()
                    if cell and len(cell) > 2:
                        # Clean up cell content
                        cell = re.sub(r'\{+', '{', cell)
                        cell = re.sub(r'\}+', '}', cell)
                        
                        # Extract mathematical expressions (ignore pure formatting)
                        if any(char in cell for char in '+-*/^=()[]'):
                            expressions.append(cell)
            
            # If we found expressions, try to parse the first meaningful one
            for expr in expressions:
                try:
                    cleaned = self._clean_expression_for_parsing(expr)
                    if cleaned and len(cleaned) > 1:
                        return sp.sympify(cleaned)
                except:
                    continue
            
            # Fallback to symbolic representation
            return sp.Symbol('complex_array_expression')
            
        except Exception as e:
            print(f"Array parsing failed: {e}")
            return sp.Symbol('array_expression')
    
    def _clean_expression_for_parsing(self, expr: str) -> str:
        """Clean expression for SymPy parsing"""
        
        # Remove complex LaTeX formatting
        expr = re.sub(r'\\overline\{([^}]+)\}', r'\1', expr)
        expr = re.sub(r'\\cal\{([^}]+)\}', r'\1', expr)
        expr = re.sub(r'\\langle([^\\]+)\\rangle', r'(\1)', expr)
        
        # Handle fractions
        expr = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1)/(\2)', expr)
        
        # Handle powers
        expr = re.sub(r'\^\{([^}]+)\}', r'**(\1)', expr)
        expr = re.sub(r'\^([a-zA-Z0-9])', r'**\1', expr)
        
        # Handle subscripts (convert to variable names)
        expr = re.sub(r'([a-zA-Z]+)_\{([^}]+)\}', r'\1_\2', expr)
        expr = re.sub(r'([a-zA-Z]+)_([a-zA-Z0-9])', r'\1_\2', expr)
        
        # Convert Greek letters
        greek_map = {
            r'\\gamma': 'gamma', r'\\alpha': 'alpha', r'\\beta': 'beta',
            r'\\delta': 'delta', r'\\epsilon': 'epsilon', r'\\varepsilon': 'epsilon',
            r'\\lambda': 'lambda', r'\\mu': 'mu', r'\\nu': 'nu',
            r'\\pi': 'pi', r'\\theta': 'theta', r'\\sigma': 'sigma'
        }
        for latex_greek, english in greek_map.items():
            expr = re.sub(latex_greek, english, expr)
        
        # Remove remaining LaTeX commands
        expr = re.sub(r'\\[a-zA-Z]+', '', expr)
        
        # Clean up formatting
        expr = expr.replace('{', '(').replace('}', ')')
        expr = re.sub(r'[^\w\d\+\-\*\/\(\)\.\=\,\_]', '', expr)
        expr = expr.replace(' ', '')
        
        return expr
    
    async def _analyze_expression(self, expr: sp.Expr, original_latex: str) -> Dict[str, Any]:
        """Analyze SymPy expression for mathematical properties"""
        
        analysis = {
            "type": self._classify_expression(expr),
            "variables": [str(v) for v in expr.free_symbols],
            "constants": [],
            "degree": None,
            "is_polynomial": expr.is_polynomial(),
            "is_rational": expr.is_rational_function(),
        }
        
        # Get numeric constants
        for atom in expr.atoms():
            if atom.is_number and not atom.is_symbol:
                analysis["constants"].append(str(atom))
        
        # For polynomials, get degree
        if analysis["is_polynomial"] and analysis["variables"]:
            try:
                main_var = sp.Symbol(analysis["variables"][0])
                poly = sp.Poly(expr, main_var)
                analysis["degree"] = poly.degree()
            except:
                pass
        
        # Check for special forms
        analysis["special_forms"] = []
        
        if expr.has(sp.sin, sp.cos, sp.tan):
            analysis["special_forms"].append("trigonometric")
        
        if expr.has(sp.exp, sp.log):
            analysis["special_forms"].append("exponential/logarithmic")
        
        if expr.has(sp.sqrt):
            analysis["special_forms"].append("radical")
        
        return analysis
    
    def _classify_expression(self, expr: sp.Expr) -> str:
        """Classify the type of mathematical expression"""
        
        if expr.is_number:
            return "constant"
        elif expr.is_symbol:
            return "variable"
        elif expr.is_Add:
            return "sum"
        elif expr.is_Mul:
            return "product"
        elif expr.is_Pow:
            return "power"
        elif expr.has(sp.sin, sp.cos, sp.tan):
            return "trigonometric"
        elif expr.has(sp.exp, sp.log):
            return "exponential"
        elif expr.is_polynomial():
            return "polynomial"
        elif expr.is_rational_function():
            return "rational"
        else:
            return "general"
