import numpy
import random
import sympy as sp
from sympy import factor, expand
from PyQt6.QtGui import QPixmap, QImage
from matplotlib import pyplot as plt
from io import BytesIO
from backend import Crand


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
        # Make a linear equation using the coefficients
        equation = f"({coeffs['a1']}*x {random.choice(['+', '-'])} {coeffs['b1']}*y) {random.choice(['+', '-'])} ({coeffs['a2']}*x {random.choice(['+', '-'])} {coeffs['b2']}*y)"
    elif difficulty == "Medium":
        # Generate random coefficients
        coeffs = {
            'a': random.randint(-10, 10),
            'b': random.randint(-10, 10),
            'c': random.randint(10, 20)
        }
        # Make a medium linear equation
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
        # Make a hard linear equation
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
            # Make the equation using the coefficients
            equation = f"({coeffs['a1']}*x {random.choice(['+', '-'])} {coeffs['b1']})*({coeffs['a2']}*x {random.choice(['+', '-'])} {coeffs['b2']})"
        else:
            # Generate two non-zero random integers
            num1, num2 = Crand.non_zero_randint(lower, upper), Crand.non_zero_randint(lower, upper)
            # Make the equation as a product of two binomials
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
            # Make a harder quadratic equation with a negative coefficient
            equation = (-x - x1) * (x - x2)
            # Intercepts for plotting
            intercepts = (-x1, x2)
        else:
            # Make a quadratic equation
            equation = (x - x1) * (x - x2)
            # Intercepts for plotting
            intercepts = (x1, x2)
        return equation, intercepts

    if difficulty == "Easy":
        # Generate an easy quadratic equation
        equation, intercepts = generate_equation(1, 5)
    elif difficulty == "Medium":
        # Generate a medium quadratic equation
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

    # Remove the axes for a better looking graph
    plt.axis('off')

    # Add labels for the intercepts in the top-right corner
    plt.text(0.95, 0.9, f"Y-intercept: (0, {y_intercept})", transform=ax.transAxes, ha='right')
    plt.text(0.95, 0.85, f"X-intercepts: ({intercepts[0]}, 0), ({intercepts[1]}, 0)", transform=ax.transAxes,
             ha='right')

    # Save the figure to a bytes buffer in PNG format
    buf = BytesIO()
    plt.savefig(buf, format='svg', bbox_inches='tight', transparent=True)
    plt.close(fig)
    buf.seek(0)

    # Load the image from the buffer into a QImage
    image = QImage()
    image.loadFromData(buf.read())
    # Convert the QImage to a QPixmap to display it
    pixmap_answer = QPixmap.fromImage(image)

    return difficulty, equation_text, pixmap_answer


def completing_square_and_turning_point(difficulty):
    # Define symbolic variable x
    x = sp.symbols('x')

    def generate_quadratic(lower_a, upper_a, lower_h, upper_h, lower_c, upper_c):
        # Generate a non-zero random integer for 'a'
        a = Crand.non_zero_randint(lower_a, upper_a)

        # Generate a random integer for 'h' (turning point x-coordinate)
        h = random.randint(lower_h, upper_h)

        # Calculate 'b' to ensure that h = -b/(2a) is an integer
        b = -2 * a * h

        # Generate a random integer for 'c'
        c = random.randint(lower_c, upper_c)

        # Make the quadratic equation
        equation = a * x ** 2 + b * x + c
        return equation, a, b, c, h

    if difficulty == "Easy":
        # Generate an easy quadratic equation
        equation, a, b, c, h = generate_quadratic(lower_a=1, upper_a=5,
                                                  lower_h=1, upper_h=5,
                                                  lower_c=1, upper_c=20)
    elif difficulty == "Medium":
        # Generate a medium quadratic equation
        equation, a, b, c, h = generate_quadratic(lower_a=1, upper_a=5,
                                                  lower_h=-5, upper_h=5,
                                                  lower_c=-20, upper_c=20)
    elif difficulty == "Hard":
        # Generate a hard quadratic equation
        equation, a, b, c, h = generate_quadratic(lower_a=1, upper_a=10,
                                                  lower_h=-10, upper_h=10,
                                                  lower_c=-30, upper_c=30)
    else:
        # Return an error message if difficulty is unknown <- Validation
        return "Unknown difficulty", None, None

    # Calculate the y-coordinate of the turning point
    k = a * h ** 2 + b * h + c

    # Completed square form: a(x - h)^2 + k
    completed_square = a * (x - h) ** 2 + k

    # Format the completed square for display
    equation_text = str(completed_square).replace('**', '^').replace('*', '')

    # Define the turning point
    answer = f"Turning Point: ({h}, {k})"

    return difficulty, equation_text, answer


def solving_quadratic_inequality(difficulty):

    # Define symbolic variable x
    x = sp.symbols('x')

    def generate_quadratic(lower_a, upper_a, lower_r, upper_r):
        """
        Generates a quadratic equation

        Parameters:
            lower_a (int): Absolute lower bound for coefficient 'a'.
            upper_a (int): Absolute upper bound for coefficient 'a'.
            lower_r (int): Lower bound for roots.
            upper_r (int): Upper bound for roots.

        Returns:
            tuple: (equation, a, r1, r2)
        """
        # Generate a random non-zero integer for 'a' (can be negative or positive)
        a = Crand.non_zero_randint(-upper_a, upper_a)

        # Generate two distinct integer roots
        r1 = random.randint(lower_r, upper_r)
        r2 = random.randint(lower_r, upper_r)
        while r2 == r1:
            r2 = random.randint(lower_r, upper_r)

        # Sort roots for consistency
        r1, r2 = sorted([r1, r2])

        # Construct the quadratic equation: a*(x - r1)*(x - r2)
        equation = a * (x - r1) * (x - r2)
        return equation, a, r1, r2

    # Choose a random inequality sign
    inequality_sign = random.choice(['<', '<=', '>', '>='])

    # Generate a quadratic equation based on the difficulty
    if difficulty == "Easy":
        # Coefficient 'a' is between -5 to -1 and 1 to 5
        # Roots between 1 and 5
        equation, a, r1, r2 = generate_quadratic(
            lower_a=1, upper_a=5,
            lower_r=1, upper_r=5
        )
    elif difficulty == "Medium":
        # Coefficient 'a' is between -5 to -1 and 1 to 5
        # Roots between -5 and 5
        equation, a, r1, r2 = generate_quadratic(
            lower_a=1, upper_a=5,
            lower_r=-5, upper_r=5
        )
    elif difficulty == "Hard":
        # Coefficient 'a' is between -10 to -1 and 1 to 10
        # Roots between -10 and 10
        equation, a, r1, r2 = generate_quadratic(
            lower_a=1, upper_a=10,
            lower_r=-10, upper_r=10
        )
    else:
        # Return error if difficulty is unknown
        return "Unknown difficulty", None, None

    # Expand the quadratic equation
    expanded_eq = sp.expand(equation)

    # Create the inequality string
    inequality_str = f"{expanded_eq} {inequality_sign} 0"
    inequality_str = str(inequality_str).replace('**', '^').replace('*', '')

    # Determine the solution set based on the sign of 'a' and the inequality
    # "\\ " means empty space
    if a > 0:
        if inequality_sign in ['>', '>=']:
            solution = f"x < {r1}\\ or\\ x > {r2}"
            if inequality_sign == '>=':
                solution += f"\\ (including\\ {r1}\\ and\\ {r2})"
        elif inequality_sign in ['<', '<=']:
            solution = f"{r1} < x < {r2}"
            if inequality_sign == '<=':
                solution += f"\\ (including\\ {r1}\\ and\\ {r2})"
    else:  # a < 0
        if inequality_sign in ['>', '>=']:
            solution = f"{r1} < x < {r2}"
            if inequality_sign == '>=':
                solution += f"\\ (including\\ {r1}\\ and\\ {r2})"
        elif inequality_sign in ['<', '<=']:
            solution = f"x < {r1}\\ or\\ x > {r2}"
            if inequality_sign == '<=':
                solution += f"\\ (including\\ {r1}\\ and\\ {r2})"

    return difficulty, inequality_str, solution

