from flask import Flask, request, jsonify
import sympy
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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

        elif exponent.is_Pow and exponent.exp == -1 and not exponent.base.is_constant():
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

def parse_custom_root_input(expression_str):
    def replace_root_syntax(match):
        root_part = match.group(1)
        base_part = match.group(2)
        return f"({base_part})**(1/{root_part})"
    
    temp_str = expression_str.replace(" ", "") 
    
    processed_str = re.sub(r'\(([^()]+)\)#([a-zA-Z0-9_.]+)', replace_root_syntax, temp_str)
    
    return processed_str

def solve_equations_general(equation_strings_list):
    sympy_equations = []
    all_symbols = set()

    for eq_str_raw in equation_strings_list:
        eq_str_parsed = parse_custom_root_input(eq_str_raw)
        
        if '=' in eq_str_parsed:
            lhs_str, rhs_str = eq_str_parsed.split('=', 1)
            sym_eq = sympy.sympify(lhs_str) - sympy.sympify(rhs_str)
        else:
            sym_eq = sympy.sympify(eq_str_parsed)

        sympy_equations.append(sym_eq)
        all_symbols.update(sym_eq.free_symbols)

    if not sympy_equations:
        return {"success": False, "message": "No equations provided."}
    
    if not all_symbols and not sympy_equations[0].is_constant():
        return {"success": False, "message": "No variables found to solve for. Please ensure your equation contains variables."}

    try:
        solutions_raw = sympy.solve(sympy_equations, list(all_symbols), dict=True)
        
        if not solutions_raw:
            if sympy_equations and all(eq.is_constant() and eq != 0 for eq in sympy_equations):
                 return {"success": False, "message": "The equations lead to a contradiction (no solution)."}
            elif sympy_equations and all(eq.is_constant() and eq == 0 for eq in sympy_equations):
                 return {"success": True, "message": "The equations are consistent but underdetermined (infinite solutions).", "solutions": []} 
            else:
                return {"success": False, "message": "No explicit solutions found or equations are underdetermined without simple solutions."}

        formatted_solutions = []
        for sol_dict in solutions_raw:
            formatted_sol = {}
            for var, val in sol_dict.items():
                formatted_sol[str(var)] = format_solution_for_display(val)
            formatted_solutions.append(formatted_sol)
            
        return {"success": True, "solutions": formatted_solutions, "message": "Equations solved successfully."}

    except Exception as e:
        return {"success": False, "message": f"An error occurred during solving: {e}"}

@app.route('/solve', methods=['POST'])
def solve_math():
    data = request.json
    
    expressions_input = data.get('expressions') 

    if not expressions_input:
        return jsonify({
            "success": False,
            "message": "No expression(s) provided."
        }), 400

    if isinstance(expressions_input, str):
        expressions_list = [expressions_input]
    elif isinstance(expressions_input, list):
        expressions_list = expressions_input
    else:
        return jsonify({
            "success": False,
            "message": "Invalid input format. 'expressions' must be a string or a list of strings."
        }), 400

    result_data = solve_equations_general(expressions_list)

    if result_data["success"]:
        return jsonify({
            "success": True,
            "solutions": result_data["solutions"],
            "message": result_data["message"]
        })
    else:
        return jsonify({
            "success": False,
            "message": result_data["message"]
        }), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)