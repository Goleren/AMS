# app.py
from flask import Flask, request, jsonify
from sympy import sympify, solve, Eq, Symbol
from flask_cors import CORS 

app = Flask(__name__)
CORS(app) 

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