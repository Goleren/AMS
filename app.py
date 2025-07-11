from flask import Flask, request, jsonify
import sympy
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

from sympy.printing.printer import Printer
class CustomRootPrinter (Printer):
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
    # This might conflict with decimal numbers if not careful.
    # For a math solver, it's generally safer to assume '.' is a decimal point
    # unless specifically parsed for multiplication context (which is complex).
    # For simplicity and given the example, we'll keep it for now.
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
                    return {"success": True, "result": f"{printer.doprint(symbol)} = {', '.join(formatted_solutions)}", "explanation": "Solution(s) found for the equation."}
            else:
                # Multi-variable equation (SymPy solve can handle systems, but for single eq, it gives implicit solutions)
                # It's generally not ideal to use solve on a single multi-variable equation
                # if you expect explicit solutions for all variables.
                # SymPy might return solutions in terms of other variables.
                solutions = sympy.solve(equation_sym, free_symbols)
                if solutions:
                    printer = CustomRootPrinter()
                    formatted_solutions = []
                    # SymPy's solve for single multi-variable equation often returns a list of dictionaries
                    # or tuples representing solution sets.
                    for sol_set in solutions:
                        if isinstance(sol_set, dict):
                            formatted_sol = ", ".join([f"{printer.doprint(k)} = {printer.doprint(v)}" for k, v in sol_set.items()])
                        else: # Can be a tuple for multiple solutions per variable, or other SymPy output
                            formatted_sol = str(sol_set) # Fallback to default string representation
                        formatted_solutions.append(formatted_sol)
                    return {"success": True, "result": "Solutions for multiple variables: " + "; ".join(formatted_solutions), "explanation": "The equation has multiple variables and solutions are expressed implicitly or parametrically."}
                else:
                    return {"success": True, "result": "No explicit solution found for multiple variables", "explanation": "Could not find explicit solutions for the given multi-variable equation."}

        else:
            # It's an expression
            expression_sym = sympy.sympify(parsed_input, evaluate=False) # evaluate=False to prevent immediate simplification before custom printer

            # Check for free symbols in the expression
            free_symbols = list(expression_sym.free_symbols)

            printer = CustomRootPrinter()
            result_str = printer.doprint(expression_sym) # Use custom printer for output

            if not free_symbols:
                # If no free symbols, evaluate to a numerical value
                # Use evaluate=True here to get numerical result after initial parse
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

# --- BỔ SUNG: Route mới để xử lý Hệ Phương Trình ---
@app.route('/solve_system', methods=['POST'])
def solve_system_math():
    data = request.json
    # Expect 'equations' as a list of strings
    equations_input = data.get('equations') 
    
    if not equations_input or not isinstance(equations_input, list):
        return jsonify({
            "success": False,
            "message": "Invalid input format.",
            "explanation": "Please provide a list of mathematical equations (e.g., ['x+y=5', 'x-y=1']) to solve."
        }), 400

    try:
        sympy_equations = []
        all_symbols = set() # Collect all unique symbols across all equations

        for eq_str in equations_input:
            if not isinstance(eq_str, str):
                return jsonify({"success": False, "message": "Invalid equation format.", "explanation": f"Each equation in the list must be a string. Found: {type(eq_str)}."}), 400

            parsed_eq_str = parse_custom_root_input(eq_str)
            if '=' not in parsed_eq_str:
                return jsonify({"success": False, "message": "Invalid equation.", "explanation": f"'{eq_str}' is not a valid equation (missing '=' sign)."}), 400
            
            lhs_str, rhs_str = parsed_eq_str.split('=')
            
            # Use evaluate=False for initial sympify to prevent premature evaluation
            # Use local_dict to define symbols if they aren't automatically recognized
            lhs = sympy.sympify(lhs_str, evaluate=False)
            rhs = sympy.sympify(rhs_str, evaluate=False)
            
            eq = sympy.Eq(lhs, rhs)
            sympy_equations.append(eq)
            all_symbols.update(eq.free_symbols) # Add symbols from this equation

        if not sympy_equations:
            return jsonify({"success": True, "result": "No equations provided.", "explanation": "The input list was empty."})

        # Convert set of symbols to a list for sympy.solve
        symbols_to_solve = list(all_symbols)
        
        # If there are no symbols to solve for (e.g., system like [2+3=5, 4+1=5])
        if not symbols_to_solve:
            # Check consistency of the system
            is_consistent = True
            for eq_sym in sympy_equations:
                if eq_sym.simplify() == False: # If any equation is inherently false (e.g., 2=3)
                    is_consistent = False
                    break
            if is_consistent:
                return jsonify({"success": True, "result": "System is consistent (all true statements).", "explanation": "The system contains no variables and is consistent."})
            else:
                return jsonify({"success": True, "result": "System is inconsistent (contains false statements).", "explanation": "The system contains no variables and is inconsistent."})


        solutions = sympy.solve(sympy_equations, symbols_to_solve)

        printer = CustomRootPrinter()
        formatted_solutions = []

        if isinstance(solutions, dict): # Single solution set (e.g., {'x': 1, 'y': 2})
            formatted_sol = ", ".join([f"{printer.doprint(k)} = {printer.doprint(v)}" for k, v in solutions.items()])
            formatted_solutions.append(formatted_sol)
        elif isinstance(solutions, list): # Multiple solution sets (e.g., for non-linear systems)
            if not solutions:
                # This could mean no solution or infinite solutions (if it simplifies to 0=0)
                # sympy.solve returns [] for no solutions and [Reals] for x=x.
                # For systems, [] means no solution. For infinite solutions, it usually returns a generic solution set
                # or conditions.
                return jsonify({"success": True, "result": "No solution for the system", "explanation": "The system of equations has no explicit solution."})
            
            # Check for generic solution (infinite solutions)
            # This is a bit tricky for systems, but if solve returns a single element list
            # where that element is an empty dictionary or contains generic symbols, it might imply infinite.
            # For simplicity, if it's not a dict, we'll stringify.
            
            for sol_set in solutions:
                if isinstance(sol_set, dict):
                    formatted_sol = ", ".join([f"{printer.doprint(k)} = {printer.doprint(v)}" for k, v in sol_set.items()])
                else: # Fallback for other formats (e.g., tuples for multiple solutions per variable)
                    formatted_sol = str(sol_set)
                formatted_solutions.append(formatted_sol)
            
            if len(formatted_solutions) == 1 and formatted_solutions[0] == "[]":
                 # This can happen if sympy.solve returns something like [[]] meaning no solutions for some reason.
                 # Reconfirming the no solution case.
                 return jsonify({"success": True, "result": "No solution for the system", "explanation": "The system of equations has no explicit solution."})

        
        # Check for cases like infinite solutions (e.g., if one equation is a multiple of another)
        if len(symbols_to_solve) > len(sympy_equations) and not solutions:
             return jsonify({
                "success": True, 
                "result": "Infinite solutions or underdetermined system", 
                "explanation": "The system might have infinite solutions or is underdetermined (more variables than independent equations)."
            })
        elif len(formatted_solutions) == 0:
            return jsonify({
                "success": True,
                "result": "No explicit solution found for the system",
                "explanation": "SymPy could not find explicit solutions for the given system. It might be inconsistent or have infinite solutions expressible parametrically."
            })

        return jsonify({
            "success": True,
            "result": "System solutions: " + "; ".join(formatted_solutions),
            "explanation": "Solutions found for the system of equations."
        })

    except (sympy.SympifyError, TypeError, ValueError) as e:
        return jsonify({"success": False, "message": "Invalid System Input", "explanation": f"Please check your equations syntax. Error: {e}"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": "An unexpected error occurred", "explanation": f"Details: {e}"}), 500


if __name__ == '__main__':
    app.run(debug=True)