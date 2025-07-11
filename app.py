from flask import Flask, request, jsonify
import sympy
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

class CustomRootPrinter(sympy.Printer):
    """
    A custom SymPy printer to format root expressions
    from sympy.Pow objects into a custom '(root_val)#base' string format.
    """
    def _print_Pow(self, expr):
        base = expr.base
        exponent = expr.exp
        
        # Case: Nth root (e.g., (2)#x for sqrt(x), (3)#x for cbrt(x))
        if isinstance(exponent, sympy.Rational) and exponent.p == 1:
            root_val = exponent.q
            formatted_base = self._print(base)
            return f"({root_val})#{formatted_base}"

        # Default SymPy printing for other power forms
        return super()._print_Pow(expr)

def parse_custom_root_input(expression):
    """
    Parses custom root notations (e.g., '2#x', '(2)#x') and
    implicit multiplications into SymPy-compatible format.
    """
    processed_str = str(expression)
    
    # Convert 'digit#base' to 'base**(1/digit)'
    # Example: 2#x -> x**(1/2)
    processed_str = re.sub(r'(\d+)#([a-zA-Z0-9_.]+)', r'\2**(1/\1)', processed_str)
    
    # Also handle '(digit)#base' for more explicit roots
    # Example: (2)#x -> x**(1/2)
    processed_str = re.sub(r'\(([^()]+)\)#([a-zA-Z0-9_.]+)', r'\2**(1/\1)', processed_str)
    
    # Handle implicit multiplication like '2x' or '3(x+1)'
    processed_str = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', processed_str)
    
    # Handle implicit multiplication like 'x(y+z)'
    processed_str = re.sub(r'([a-zA-Z])(\()', r'\1*\2', processed_str)
    
    # Handle 'a.b' as 'a*b'
    processed_str = processed_str.replace('.', '*')
    
    return processed_str

def solve_expression_or_equation(input_str):
    """
    Solves a given mathematical expression or equation using SymPy.
    Handles expressions, single-variable equations, and multi-variable equations.
    """
    try:
        # Pre-process input for custom root and implicit multiplication
        parsed_input = parse_custom_root_input(input_str)

        # Check if the input contains an equality sign to determine if it's an equation
        if '=' in parsed_input:
            # It's an equation
            parts = parsed_input.split('=')
            if len(parts) != 2:
                return {"success": False, "result": "Invalid Equation", "explanation": "Equations must have exactly one '=' sign."}
            
            lhs = sympy.sympify(parts[0], evaluate=False)
            rhs = sympy.sympify(parts[1], evaluate=False)
            equation_sym = sympy.Eq(lhs, rhs)
            
            # Find all free symbols in the equation
            free_symbols = list(equation_sym.free_symbols)
            
            if not free_symbols:
                # If no free symbols, evaluate the boolean expression
                result = sympy.simplify(equation_sym)
                if result == True:
                    return {"success": True, "result": "True", "explanation": "The statement is always true."}
                elif result == False:
                    return {"success": True, "result": "False", "explanation": "The statement is always false."}
                else:
                    return {"success": True, "result": str(result), "explanation": "Evaluated as a boolean expression."}

            elif len(free_symbols) == 1:
                # Single variable equation
                symbol = free_symbols[0]
                solutions = sympy.solve(equation_sym, symbol)
                
                if not solutions:
                    return {"success": True, "result": "No solution", "explanation": "The equation has no solution."}
                elif solutions == [sympy.S.Reals]: # Check for all real numbers as solution (SymPy's representation for x=x)
                     return {"success": True, "result": "Infinite solutions (all real numbers)", "explanation": "The equation is true for all real numbers."}
                else:
                    # Use the custom printer for solutions that are Pow objects (roots)
                    printer = CustomRootPrinter()
                    formatted_solutions = [printer.doprint(sol) for sol in solutions]
                    return {"success": True, "result": f"x = {', '.join(formatted_solutions)}", "explanation": "Solution(s) found for the equation."}
            else:
                # Multi-variable equation (SymPy solve can handle systems, but for single eq, it gives implicit solutions)
                solutions = sympy.solve(equation_sym, free_symbols)
                if solutions:
                    # Attempt to provide a simplified form or show relationships
                    # For multi-variable, solution is often a dictionary or list of dicts
                    printer = CustomRootPrinter()
                    formatted_solutions = []
                    for sol_set in solutions:
                        if isinstance(sol_set, dict):
                            formatted_sol = ", ".join([f"{printer.doprint(k)} = {printer.doprint(v)}" for k, v in sol_set.items()])
                        else: # Can be a tuple for multiple solutions per variable
                            formatted_sol = str(sol_set) # Fallback to default string
                        formatted_solutions.append(formatted_sol)
                    return {"success": True, "result": "Solutions for multiple variables", "explanation": f"The equation has multiple variables: {'; '.join(formatted_solutions)}"}
                else:
                    return {"success": True, "result": "No obvious solution for multiple variables", "explanation": "Could not find explicit solutions for the given multi-variable equation."}

        else:
            # It's an expression
            expression_sym = sympy.sympify(parsed_input, evaluate=False) # evaluate=False to prevent immediate simplification before custom printer

            # Check for free symbols in the expression
            free_symbols = list(expression_sym.free_symbols)

            printer = CustomRootPrinter()
            result_str = printer.doprint(expression_sym) # Use custom printer for output

            if not free_symbols:
                # If no free symbols, evaluate to a numerical value
                # Use evaluate=True here to get numerical result
                evaluated_result = sympy.sympify(parsed_input) 
                explanation = f"This is an arithmetic expression. The result is calculated."
                return {"success": True, "result": str(evaluated_result), "explanation": explanation}
            else:
                # If there are free symbols, simplify the expression
                simplified_expression = sympy.simplify(expression_sym)
                explanation = f"This is an algebraic expression. The simplified form is shown."
                return {"success": True, "result": printer.doprint(simplified_expression), "explanation": explanation}

    except (sympy.SympifyError, TypeError, ValueError) as e:
        return {"success": False, "result": "Invalid Input", "explanation": f"Please check your math expression or equation syntax. Error: {e}"}
    except Exception as e:
        return {"success": False, "result": "An unexpected error occurred", "explanation": f"Please try again or simplify your input. Details: {e}"}

@app.route('/solve', methods=['POST'])
def solve_math():
    data = request.json
    
    # Changed from 'expressions' to 'expression' to expect a single string
    expression_input = data.get('expression') 

    if not expression_input:
        return jsonify({
            "success": False,
            "message": "No expression provided.",
            "explanation": "Please enter a mathematical expression or equation to solve."
        }), 400

    if not isinstance(expression_input, str):
        return jsonify({
            "success": False,
            "message": "Invalid input format. 'expression' must be a string.",
            "explanation": "The provided input type is not supported. Please send your math problem as a text string."
        }), 400

    # Call the new unified solving function
    result_data = solve_expression_or_equation(expression_input)

    if result_data["success"]:
        return jsonify({
            "success": True,
            "result": result_data["result"],
            "explanation": result_data["explanation"]
        })
    else:
        return jsonify({
            "success": False,
            "message": result_data["result"], # Use 'result' field for short error message
            "explanation": result_data["explanation"] # Use 'explanation' for detailed error
        }), 400 # Return 400 for client-side errors

if __name__ == '__main__':
    app.run(debug=True)