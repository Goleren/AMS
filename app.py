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

        # Case: x^(-1/n) type roots if needed, but the first case handles most 1/n exponents.
        # This part might be redundant if the first case is comprehensive enough for 1/n.
        elif isinstance(exponent, sympy.Pow) and exponent.exp == -1:
            root_val = exponent.base
            formatted_base = self._print(base)
            return f"({root_val})#{formatted_base}"
        
        # Case: 1/variable root (e.g., x**(1/y) where y is a symbol)
        elif exponent.is_Pow and exponent.exp == -1 and not exponent.base.is_constant():
            root_val = exponent.base
            formatted_base = self._print(base)
            formatted_root = self._print(root_val)
            return f"({formatted_root})#{formatted_base}"

        # Default behavior for other power expressions
        return super()._print_Pow(expr)

    # You can add more custom print methods if needed for other SymPy objects
    # def _print_Add(self, expr):
    #     return super()._print_Add(expr)

    # def _print_Mul(self, expr):
    #     return super()._print_Mul(expr)

# Instantiate the custom printer
my_root_printer = CustomRootPrinter()

def format_solution_for_display(sym_expr):
    """Formats a SymPy expression for display using the custom printer."""
    return my_root_printer.doprint(sym_expr)

def parse_custom_root_input(expression_str):
    """
    Converts custom root syntax (e.g., (2)#x) to SymPy compatible format (x**(1/2)).
    Also handles "a.b" to "a*b" and "2a" to "2*a" for simpler input.
    """
    # Remove spaces
    temp_str = expression_str.replace(" ", "") 
    
    # Replace custom root syntax (e.g., (2)#x -> (x)**(1/2))
    # This regex is specifically for (root_index)#base_expression
    # It assumes base_expression does not contain #
    processed_str = re.sub(r'\(([^()]+)\)#([a-zA-Z0-9_.]+)', r'\2**(1/\1)', temp_str)
    
    # Handle implicit multiplication: 2x -> 2*x, 3(x+1) -> 3*(x+1)
    # This also converts 'a.b' to 'a*b'
    # Pattern: digit followed by a letter/parenthesis OR letter followed by parenthesis
    processed_str = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', processed_str)
    processed_str = re.sub(r'([a-zA-Z])(\()', r'\1*\2', processed_str)
    
    # Replace '.' with '*' for multiplication
    processed_str = processed_str.replace('.', '*')
    
    return processed_str

def solve_expression_or_equation(expression_str_raw):
    """
    Solves a single mathematical expression or equation and provides an explanation.
    """
    explanation = ""
    result = ""
    success = True
    
    try:
        # Step 1: Pre-process custom input syntax
        processed_expression = parse_custom_root_input(expression_str_raw)
        
        # Determine if it's an equation or just an expression
        if '=' in processed_expression:
            # It's an equation
            lhs_str, rhs_str = processed_expression.split('=', 1)
            
            # Step 2: SymPyfying (parsing) the equation
            lhs = sympy.sympify(lhs_str)
            rhs = sympy.sympify(rhs_str)
            equation_sym = sympy.Eq(lhs, rhs)
            
            # Identify free symbols (variables)
            free_symbols = list(equation_sym.free_symbols)
            
            if not free_symbols:
                # Case: Equation with no variables (e.g., 2 + 3 = 5 or 2 = 3)
                if equation_sym.is_Relational: # Check if it's a relation (e.g., Eq, Gt, Lt)
                    if equation_sym == True: # If 2+3=5 evaluates to True
                        result = "Equation is always true (Identity)."
                        explanation = f"The equation '{expression_str_raw}' simplifies to a true statement, meaning it is an identity. For example, both sides of the equation might simplify to the same constant value."
                    else: # If 2=3 evaluates to False
                        result = "Equation is false (Contradiction)."
                        explanation = f"The equation '{expression_str_raw}' simplifies to a false statement, meaning there is no solution. For example, it might simplify to '0 = 5'."
                else:
                    # Should not happen if '=' is present and it's not a relational, but for safety:
                    result = "Error: Invalid equation format or no identifiable relation."
                    explanation = "The input appears to be an equation but could not be parsed as a valid relational expression."
                success = False
            else:
                # Attempt to solve the equation
                solutions_raw = sympy.solve(equation_sym, free_symbols)
                
                if not solutions_raw:
                    result = "No solutions found or infinite solutions."
                    explanation = f"SymPy could not find explicit solutions for the equation '{expression_str_raw}'. This might mean there are no solutions, or there are infinitely many solutions (e.g., an identity like x = x), or the equation is too complex for SymPy to solve explicitly."
                    # Refine explanation for identities if possible
                    if len(free_symbols) == 1 and sympy.simplify(lhs - rhs) == 0:
                        result = "Equation is an identity (infinite solutions)."
                        explanation = f"The equation '{expression_str_raw}' simplifies to '0 = 0' or a similar identity, meaning it is true for all possible values of '{free_symbols[0]}'. Thus, it has infinitely many solutions."
                else:
                    # Format solutions
                    if len(free_symbols) == 1:
                        var_name = str(free_symbols[0])
                        if isinstance(solutions_raw, list):
                            if len(solutions_raw) == 1:
                                result = f"{var_name} = {format_solution_for_display(solutions_raw[0])}"
                                explanation = f"The equation was solved for '{var_name}'. Substituting this value back into the original equation will make both sides equal."
                            elif len(solutions_raw) > 1:
                                formatted_sols = [format_solution_for_display(sol) for sol in solutions_raw]
                                result = f"{var_name} = " + ", ".join(formatted_sols)
                                explanation = f"The equation has multiple solutions for '{var_name}'. Each of these values will satisfy the original equation."
                            else: # Empty list for single variable after solve, meaning no solution
                                result = "No solution found for this equation."
                                explanation = "SymPy could not find any explicit solution for the variable in this equation."
                        else: # E.g., for non-linear equations, solve might return a set or dict
                            result = f"{var_name} = {format_solution_for_display(solutions_raw)}"
                            explanation = f"The equation was solved for '{var_name}'."

                    elif len(free_symbols) > 1:
                        # Handle systems of equations or multi-variable single equations
                        # sympy.solve returns a list of dictionaries for multiple variables
                        formatted_solutions = []
                        if isinstance(solutions_raw, dict): # Single solution for multiple vars
                            formatted_sol = {str(k): format_solution_for_display(v) for k, v in solutions_raw.items()}
                            formatted_solutions.append(formatted_sol)
                        elif isinstance(solutions_raw, list) and all(isinstance(s, dict) for s in solutions_raw):
                            for sol_dict in solutions_raw:
                                formatted_sol = {str(k): format_solution_for_display(v) for k, v in sol_dict.items()}
                                formatted_solutions.append(formatted_sol)
                        
                        if formatted_solutions:
                            result = "Solutions: " + str(formatted_solutions) # Use simple string conversion for dicts/lists
                            explanation = f"The equation (or system if multiple were provided) was solved for the variables {', '.join(str(s) for s in free_symbols)}. The solutions are presented as a set of assignments for each variable."
                        else:
                            result = "No explicit solutions found for multiple variables."
                            explanation = "SymPy could not find explicit solutions for the variables in this multi-variable equation. This might indicate no solutions, infinite solutions, or a complex solution space."
                    
        else:
            # It's an expression (no '=')
            expression_sym = sympy.sympify(processed_expression)
            
            # Identify free symbols (variables)
            free_symbols = list(expression_sym.free_symbols)

            if not free_symbols:
                # Case: Pure arithmetic expression (e.g., 2+3*4)
                result = format_solution_for_display(expression_sym.evalf()) # Evaluate numerically
                explanation = f"The arithmetic expression '{expression_str_raw}' was evaluated to its numerical value."
            else:
                # Case: Algebraic expression (e.g., x + 2*y)
                simplified_expr = sympy.simplify(expression_sym)
                result = format_solution_for_display(simplified_expr)
                explanation = f"The algebraic expression '{expression_str_raw}' was simplified. No specific numerical solution can be found without assigning values to variables or forming an equation."
                if simplified_expr != expression_sym:
                    explanation += f" It simplifies to: {format_solution_for_display(simplified_expr)}."

    except (sympy.SympifyError, ValueError, TypeError) as e:
        success = False
        result = "Invalid input or syntax error."
        explanation = f"Please check your expression/equation. Make sure variables are single letters or known symbols. Error details: {e}"
    except Exception as e:
        success = False
        result = "An unexpected error occurred."
        explanation = f"Something went wrong while processing your request. Please try again or simplify your input. Error details: {e}"

    return {"success": success, "result": result, "explanation": explanation}


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
        }), 400 # Return 400 for client-side errors / invalid input

if __name