# app.py
from flask import Flask, request, jsonify
from sympy import sympify, solve, Eq, Symbol
from flask_cors import CORS 

app = Flask(__name__)
CORS(app) 

import sympy
from sympy.abc import symbols
class CustomRootPrinter(sympy.Printer):
    def _print_Pow(self, expr):
        base = expr.base
        exponent = expr.exp
        if isinstance(exponent, sympy.Rational) and exponent.p == 1:
            root_val = exponent.q
            formatted_base = self._print(base)
            return f"({root_val})#{formatted_base}"
        elif isinstance(exponent, sympy.Pow) and exponent.exp == -1:
            root_val = exponent.base
            formatted_base = self._print(base)
            return f"({root_val})#{formatted_base}"
        elif exponent.is_Pow and exponent.exp == -1:
             root_val = exponent.base
             formatted_base = self._print(base)
             formatted_root = self._print(root_val)
             return f"({formatted_root})#{formatted_base}"
        return super()._print_Pow(expr)
    def _print_Add(self, expr):
        return super()._print_Add(expr)

    def _print_Mul(self, expr):
        return super()._print_Mul(expr)
my_root_printer = CustomRootPrinter()
def format_solution_for_display(sym_expr):
    return my_root_printer.doprint(sym_expr)
import re

def parse_custom_root_input(expression_str):
    def replace_root_syntax(match):
        root_part = match.group(1) 
        base_part = match.group(2)
        return f"({base_part})**(1/{root_part})"
    processed_str = re.sub(r'\( ( [a-zA-Z0-9_./+\-* ]+ ) \) # ( [a-zA-Z0-9_.]+ )', replace_root_syntax, expression_str.replace(" ", ""))
    return processed_str
def solve_multiple_equations(equation_strings):    
    sympy_equations = []
    all_symbols = set()

    for eq_str in equation_strings:
        if '=' in eq_str:
            lhs_str, rhs_str = eq_str.split('=', 1)
            sym_eq = sympy.sympify(lhs_str) - sympy.sympify(rhs_str)
        else:
            sym_eq = sympy.sympify(eq_str)

        sympy_equations.append(sym_eq)
        all_symbols.update(sym_eq.free_symbols)

    if not sympy_equations:
        return "Please enter at least one equation."
    
    if not all_symbols:
        return "No variables found to solve for."

    try:
        solutions = sympy.solve(sympy_equations, list(all_symbols))
        return solutions
    except Exception as e:
        return f"Error solving equations: {e}"
user_equation_string = "your_processed_input_string_from_user"
if '=' in user_equation_string:
    lhs_str, rhs_str = user_equation_string.split('=', 1)
    sympy_expression = sympy.sympify(lhs_str) - sympy.sympify(rhs_str)
else:
    sympy_expression = sympy.sympify(user_equation_string)
variables_to_solve = list(sympy_expression.free_symbols)
try:
    solutions = sympy.solve(sympy_expression, variables_to_solve, dict=True)
    formatted_solutions = []
    for sol_dict in solutions:
        formatted_sol = {}
        for var, val in sol_dict.items():
            formatted_val = format_solution_for_display(val)
            formatted_sol[str(var)] = formatted_val
        formatted_solutions.append(formatted_sol)
except Exception as e:
    return f"Error: {e}"
@app.route('/solve', methods=['POST'])
def solve_math():
    data = request.json
    expression = data.get('expression', '')

    if not expression:
        return jsonify({
            "success": False,
            "message": "No expression provided.",
            "explanation": "Please enter an expression to solve."
        }), 400

    try:
        expr = sympify(expression)
        result = expr.evalf() 

        explanation = f"Result of the calculation: {expression} = {result}\n\n"
        explanation += "This is a basic arithmetic operation performed."

        return jsonify({
            "success": True,
            "result": str(result),
            "explanation": explanation
        })

    except (SyntaxError, TypeError, ValueError) as e:
        try:
            x = Symbol('x')
            
            if '=' in expression:
                parts = expression.split('=')
                lhs_str = parts[0].strip()
                rhs_str = parts[1].strip()
                equation = Eq(sympify(lhs_str, locals={'x': x}), sympify(rhs_str, locals={'x': x}))
            else:
                equation = Eq(sympify(expression, locals={'x': x}), 0)

            solutions = solve(equation, x)

            explanation = f"You entered the equation: {expression}\n\n"
            if solutions:
                explanation += "The solutions for the equation are:\n"
                for i, sol in enumerate(solutions):
                    explanation += f"  x = {sol}\n"
            else:
                explanation += "No explicit solutions found or the equation has no solution/infinite solutions."
            explanation += "\nNote: SymPy is a powerful Python library for symbolic mathematics."

            return jsonify({
                "success": True,
                "result": f"Solutions: {solutions}",
                "explanation": explanation
            })

        except Exception as e_eq:
            return jsonify({
                "success": False,
                "message": "Could not solve this expression/equation.",
                "explanation": f"Error parsing equation: {e_eq}\nPlease try entering basic arithmetic or an equation in the format 'x + 5 = 10' or 'x**2 - 4 = 0'."
            }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An unexpected error occurred.",
            "explanation": f"Error details: {e}\nIt might be due to incorrect syntax or a highly complex expression."
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 