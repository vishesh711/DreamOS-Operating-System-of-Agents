"""
Calculator tool for DreamOS
"""
import math
import re
from typing import Dict, Any, Union, Optional

class CalculatorTool:
    """Simple calculator tool that safely evaluates mathematical expressions."""
    
    def __init__(self):
        """Initialize the calculator tool."""
        self.name = "calculator"
        self.description = "Performs mathematical calculations"
        self.safe_dict = {
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
            'sum': sum,
            'pow': pow,
            'len': len,
            'int': int,
            'float': float,
            # Math functions
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'asin': math.asin,
            'acos': math.acos,
            'atan': math.atan,
            'sqrt': math.sqrt,
            'log': math.log,
            'log10': math.log10,
            'exp': math.exp,
            'pi': math.pi,
            'e': math.e,
            'ceil': math.ceil,
            'floor': math.floor
        }
    
    def _clean_expression(self, expression: str) -> str:
        """
        Clean and validate the expression to ensure it's safe.
        
        Args:
            expression: The math expression string
            
        Returns:
            Cleaned expression string
        """
        # Remove any suspicious constructs
        cleaned = re.sub(r'__.*?__', '', expression)  # Remove dunder methods
        cleaned = re.sub(r'import|exec|eval|open|file|os|sys|subprocess', '', cleaned)  # Remove dangerous functions
        
        # Additional safety checks can be added here
        return cleaned
    
    def execute(self, expression: str) -> Dict[str, Any]:
        """
        Execute a mathematical expression.
        
        Args:
            expression: The math expression to evaluate
            
        Returns:
            Dictionary with result or error
        """
        try:
            # Clean and validate the expression
            cleaned_expr = self._clean_expression(expression)
            
            # Evaluate the expression in a safe context
            result = eval(cleaned_expr, {"__builtins__": {}}, self.safe_dict)
            
            return {
                "status": "success",
                "result": result,
                "expression": expression
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "expression": expression
            }
    
    def get_info(self) -> Dict[str, str]:
        """
        Get information about the calculator tool.
        
        Returns:
            Dictionary with tool information
        """
        return {
            "name": self.name,
            "description": self.description,
            "usage": "calculator.execute('2 + 2 * 4')",
            "examples": [
                "calculator.execute('2 + 2')",
                "calculator.execute('sin(pi/2)')",
                "calculator.execute('sqrt(16) + 10')"
            ]
        } 