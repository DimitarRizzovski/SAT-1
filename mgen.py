import numpy
import random
import sympy as sp
from sympy import factor, expand
from PyQt6.QtGui import QPixmap, QImage
from matplotlib import pyplot as plt
from io import BytesIO
import Crand

def custom_expand(original_equation):
    # Expand the original equation using sympy
    expanded_expression = sp.expand(original_equation)
    # Convert the expanded expression to a string and format it
    expanded_expression_str = str(expanded_expression).replace('**', '^').replace('*', '')
    # Split the expression into individual terms
    terms = expanded_expression_str.split(' + ')
    # Sort the terms to ensure x^2 terms come first
    terms.sort(key=lambda term: 'x^2' not in term)
    # Join the terms back into a single string
    return ' + '.join(terms)

def generate_linear_equation(difficulty):
    # Define variables x and y
    x, y = sp.symbols('x y')

    def expand_linear(equation):
        # Expand the equation and format it
        expanded_expression = sp.expand(equation)
        return str(expanded_expression).replace('**', '^').replace('*', '')

    if difficulty == "Easy":
        # Generate random non-zero coefficients for the equation
        coeffs = {
            'a1': Crand.non_zero_randint(-20, 20),
            'b1': Crand.non_zero_randint(0, 20),
            'a2': Crand.non_zero_randint(-20, 20),
            'b2': Crand.non_zero_randint(0, 20)
        }
        # Construct a linear equation using the coefficients
        equation = f"({coeffs['a1']}*x {random.choice(['+', '-'])} {coeffs['b1']}*y) {random.choice(['+', '-'])} ({coeffs['a2']}*x {random.choice(['+', '-'])} {coeffs['b2']}*y)"
    elif difficulty == "Medium":
        # Generate random coefficients
        coeffs = {
            'a': random.randint(-10, 10),
            'b': random.randint(-10, 10),
            'c': random.randint(10, 20)
        }
        # Construct a linear equation
        equation = f"{coeffs['a']}*x*({coeffs['b']}*x {random.choice(['+', '-'])} {coeffs['c']})"
    elif difficulty == "Hard":
        # Generate more complex coefficients
        coeffs = {
            'a1': Crand.non_zero_randint(-10, 10),
            'b1': Crand.non_zero_randint(-10, 10),
            'c1': Crand.non_zero_randint(10, 20),
            'a2': Crand.non_zero_randint(0, 10),
            'b2': Crand.non_zero_randint(-10, 10),
            'c2': Crand.non_zero_randint(10, 20)
        }
        # Construct a linear equation
        equation = f"{coeffs['a1']}*x*({coeffs['b1']}*x {random.choice(['+', '-'])} {coeffs['c1']}) {random.choice(['+', '-'])} {coeffs['a2']}*x*({coeffs['b2']}*x {random.choice(['+', '-'])} {coeffs['c2']})"
    else:
        # Return an error message if difficulty is unknown <- Validation
        return "Unknown difficulty", None, None

    # Expand and format the equation
    expanded_equation = expand_linear(equation)
    equation = equation.replace('**', '^').replace('*', '')
    return difficulty, equation, expanded_equation

def generate_factorise_equation(difficulty):
    # Define variable x
    x = sp.symbols('x')

    def generate_equation(lower, upper, hard=False):
        if hard:
            # Generate random coefficients for a harder equation
            coeffs = {
                'a1': Crand.non_zero_randint(-5, 5),
                'b1': random.randint(1, 5),
                'a2': Crand.non_zero_randint(-5, 5),
                'b2': random.randint(1, 5)
            }
            # Construct the equation using the coefficients
            equation = f"({coeffs['a1']}*x {random.choice(['+', '-'])} {coeffs['b1']})*({coeffs['a2']}*x {random.choice(['+', '-'])} {coeffs['b2']})"
        else:
            # Generate two non-zero random integers
            num1, num2 = Crand.non_zero_randint(lower, upper), Crand.non_zero_randint(lower, upper)
            # Construct the equation as a product of two binomials
            equation = (x + num1) * (x + num2)
        # Expand and factor the equation
        expanded_eq = expand(equation)
        factorized_eq = factor(expanded_eq)
        # Format the equations for display
        expanded_eq_str = str(expanded_eq).replace('**', '^').replace('*', '')
        factorized_eq_str = str(factorized_eq).replace('**', '^').replace('*', '')
        return expanded_eq_str, factorized_eq_str

    if difficulty == "Easy":
        # Generate an easy factorisable equation
        equation_text, answer = generate_equation(1, 5)
    elif difficulty == "Medium":
        # Generate a medium difficulty equation
        equation_text, answer = generate_equation(-5, 5)
    elif difficulty == "Hard":
        # Generate a hard factorisable equation
        equation_text, answer = generate_equation(-5, 5, hard=True)
    else:
        # Return an error message if difficulty is unknown
        return "Unknown difficulty", None, None

    return difficulty, equation_text, answer

def construct_quadratic(difficulty):
    # Define symbolic variable x
    x = sp.symbols('x')

    def generate_equation(lower, upper):
        # Generate two non-zero random integers as roots
        x1 = Crand.non_zero_randint(lower, upper)
        x2 = Crand.non_zero_randint(lower, upper)
        # Construct the quadratic equation from roots
        equation = (x - x1) * (x - x2)
        # Format the answer with the roots
        answer = f"x = {{{x1}, {x2}}}"
        return equation, answer

    if difficulty == "Easy":
        # Generate an equation with roots between 1 and 5
        equation, answer = generate_equation(1, 5)
    elif difficulty == "Medium":
        # Generate an equation with roots between -5 and 5
        equation, answer = generate_equation(-5, 5)
    elif difficulty == "Hard":
        # Generate an equation with roots between -10 and 10
        equation, answer = generate_equation(-10, 10)
    else:
        # Return an error message if difficulty is unknown <- Validation
        return "Unknown difficulty", None, None

    # Expand and format the equation
    equation_text = str(expand(equation)).replace('**', '^').replace('*', '')
    return difficulty, equation_text, answer

def generate_graphing_quadratic(difficulty):
    # Define variable x
    x = sp.symbols('x')

    def generate_equation(lower, upper, hard=False):
        # Generate two non-zero integers, excluding zero and one
        x1 = Crand.non_zero_one_randint(lower, upper)
        x2 = Crand.non_zero_one_randint(lower, upper)
        if hard:
            # Construct a harder quadratic equation with a negative coefficient
            equation = (-x - x1) * (x - x2)
            # Intercepts for plotting
            intercepts = (-x1, x2)
        else:
            # Construct a quadratic equation
            equation = (x - x1) * (x - x2)
            # Intercepts for plotting
            intercepts = (x1, x2)
        return equation, intercepts

    if difficulty == "Easy":
        # Generate an easy quadratic equation
        equation, intercepts = generate_equation(1, 5)
    elif difficulty == "Medium":
        # Generate a medium difficulty quadratic equation
        equation, intercepts = generate_equation(-5, 5)
    elif difficulty == "Hard":
        # Generate a hard quadratic equation with negative coefficients
        equation, intercepts = generate_equation(-10, 10, hard=True)
    else:
        # Return an error message if difficulty is unknown
        return "Unknown difficulty", None, None

    # Expand the equation and format it for display
    equation_text = str(expand(equation)).replace('**', '^').replace('*', '')

    # Generate values for plotting the quadratic function
    x_vals = numpy.linspace(-15, 15, 400)
    # Evaluate the equation over the range of x values
    y_vals = sp.lambdify(x, equation, 'numpy')(x_vals)

    # Create a plot figure with a transparent background
    fig, ax = plt.subplots(figsize=(6, 5), facecolor='none')
    # Plot the quadratic curve
    ax.plot(x_vals, y_vals, color='black')
    # Draw the x-axis and y-axis lines
    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.axvline(x=0, color='black', linewidth=0.5)

    # Calculate the y-intercept (when x = 0)
    y_intercept = sp.lambdify(x, equation, 'numpy')(0)
    # Mark the y-intercept with a red dot
    ax.plot(0, y_intercept, 'ro', markersize=8)
    # Mark the x-intercepts with blue dots
    ax.plot(intercepts[0], 0, 'bo', markersize=8)
    ax.plot(intercepts[1], 0, 'bo', markersize=8)

    # Remove the axes for a cleaner look
    plt.axis('off')

    # Add labels for the intercepts in the top-right corner
    plt.text(0.95, 0.9, f"Y-intercept: (0, {y_intercept})", transform=ax.transAxes, ha='right')
    plt.text(0.95, 0.85, f"X-intercepts: ({intercepts[0]}, 0), ({intercepts[1]}, 0)", transform=ax.transAxes, ha='right')

    # Save the figure to a bytes buffer in PNG format
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    plt.close(fig)
    buf.seek(0)

    # Load the image from the buffer into a QImage
    image = QImage()
    image.loadFromData(buf.read())
    # Convert the QImage to a QPixmap for display in a PyQt application
    pixmap_answer = QPixmap.fromImage(image)

    return difficulty, equation_text, pixmap_answer
