import numpy
import Crand
from sympy import factor, expand
import sympy as sp
from PyQt6.QtGui import QPixmap, QImage
import random
from matplotlib import pyplot as plt
from io import BytesIO


# For Quadratics Expansion
def custom_expand(original_equation):
    expanded_expression = sp.expand(original_equation)
    expanded_expression_str = str(expanded_expression).replace('**', '^').replace('*', '')
    terms = expanded_expression_str.split(' + ')
    terms.sort(key=lambda term: 'x^2' not in term)
    return ' + '.join(terms)


def generate_linear_equation(difficulty):
    def expand_linear(original_equation):
        expanded_expression = sp.expand(original_equation)
        expanded_expression_str = str(expanded_expression).replace('**', '^').replace('*', '')
        return expanded_expression_str

    def generate_equation_easy():
        x, y = sp.symbols('x y')
        answer = f"({Crand.non_zero_randint(-20, 20)}*x {random.choice(['+', '-'])} {Crand.non_zero_randint(0, 20)}*y) {random.choice(['+', '-'])} ({Crand.non_zero_randint(-20, 20)}*x {random.choice(['+', '-'])} {Crand.non_zero_randint(0, 20)}*y)"
        expanded_equation = expand_linear(answer)
        answer = str(answer).replace('**', '^').replace('*', '')
        return answer, expanded_equation

    def generate_equation_medium():
        x = sp.symbols('x')
        answer = f"{random.randint(-10, 10)}*x*({random.randint(-10, 10)}*x {random.choice(['+', '-'])} {random.randint(10, 20)})"
        expanded_equation = expand_linear(answer)
        answer = str(answer).replace('**', '^').replace('*', '')
        return answer, expanded_equation

    def generate_equation_hard():
        x = sp.symbols('x')
        answer = f"{Crand.non_zero_randint(-10, 10)}*x*({Crand.non_zero_randint(-10, 10)}*x {random.choice(['+', '-'])} {Crand.non_zero_randint(10, 20)}) {random.choice(['+', '-'])} {Crand.non_zero_randint(0, 10)}*x*({Crand.non_zero_randint(-10, 10)}*x {random.choice(['+', '-'])} {Crand.non_zero_randint(10, 20)})"
        expanded_equation = expand_linear(answer)
        answer = str(answer).replace('**', '^').replace('*', '')
        return answer, expanded_equation

    if difficulty == "Easy":
        answer, expanded_equation = generate_equation_easy()
    elif difficulty == "Medium":
        answer, expanded_equation = generate_equation_medium()
    elif difficulty == "Hard":
        answer, expanded_equation = generate_equation_hard()
    else:
        answer, expanded_equation = "Unknown difficulty", None

    return difficulty, answer, expanded_equation


def generate_factorise_equation(difficulty):
    def generate_equation(lower, upper):
        x = sp.symbols('x')
        num1, num2 = Crand.non_zero_randint(lower, upper), Crand.non_zero_randint(lower, upper)
        original_equation = (x + num1) * (x + num2)
        expanded_equation = expand(original_equation)
        factorized_equation = factor(expanded_equation)
        expanded_equation = str(expanded_equation).replace("**", "^").replace("*", "")
        factorized_equation = str(factorized_equation).replace("**", "^").replace("*", "")
        return expanded_equation, factorized_equation  # Flip the order here

    def generate_equation_hard():
        x = sp.symbols('x')
        original_equation = f"({Crand.non_zero_randint(-5, 5)}*x {random.choice(['+', '-'])} {random.randint(1, 5)})*({Crand.non_zero_randint(-5, 5)}*x {random.choice(['+', '-'])} {random.randint(1, 5)})"
        expanded_equation = expand(original_equation)
        factorized_equation = factor(expanded_equation)
        expanded_equation = str(expanded_equation).replace("**", "^").replace("*", "")
        factorized_equation = str(factorized_equation).replace("**", "^").replace("*", "")
        return expanded_equation, factorized_equation  # Flip the order here

    if difficulty == "Easy":
        equation_text, answer = generate_equation(1, 5)
    elif difficulty == "Medium":
        equation_text, answer = generate_equation(-5, 5)
    elif difficulty == "Hard":
        equation_text, answer = generate_equation_hard()
    else:
        equation_text, answer = "Unknown difficulty", None

    return difficulty, equation_text, answer


def construct_quadratic(difficulty):
    def generate_equation(lower, upper):
        x = sp.symbols('x')
        x1, x2 = Crand.non_zero_randint(lower, upper), Crand.non_zero_randint(lower, upper)
        answer = (x - x1) * (x - x2)
        return answer, (x1, x2)

    def generate_equation_medium_hard(lower, upper):
        x = sp.symbols('x')
        x1, x2 = Crand.non_zero_one_randint(lower, upper), Crand.non_zero_one_randint(lower, upper)
        answer = (x - x1) * (x - x2)
        return answer, (x1, x2)

    if difficulty == "Easy":
        equation, answer = generate_equation(1, 5)
    elif difficulty == "Medium":
        equation, answer = generate_equation_medium_hard(-5, 5)
    elif difficulty == "Hard":
        equation, answer = generate_equation_medium_hard(-10, 10)
    else:
        equation, answer = "Unknown difficulty", None

    equation_text = sp.expand(equation)
    equation_text = str(equation_text).replace("**", "^").replace("*", "")

    return difficulty, equation_text, answer

def generate_graphing_quadratic(difficulty):
    def generate_equation(lower, upper):
        x = sp.symbols('x')
        x1, x2 = Crand.non_zero_one_randint(lower, upper), Crand.non_zero_one_randint(lower, upper)
        equation = (x - x1) * (x - x2)
        return equation, (x1, x2)  # Return the equation and intercepts

    def generate_equation_medium_hard(lower, upper):
        x = sp.symbols('x')
        x1, x2 = Crand.non_zero_one_randint(lower, upper), Crand.non_zero_one_randint(lower, upper)
        equation = (x - x1) * (x - x2)
        return equation, (x1, x2)  # Return the equation and intercepts

    if difficulty == "Easy":
        equation, intercepts = generate_equation(1, 5)
    elif difficulty == "Medium":
        equation, intercepts = generate_equation_medium_hard(-5, 5)
    elif difficulty == "Hard":
        equation, intercepts = generate_equation_medium_hard(-10, 10)
    else:
        equation, intercepts = "Unknown difficulty", None

    # Generate the question (expanded form of the equation)
    equation_text = sp.expand(equation)
    equation_text = str(equation_text).replace("**", "^").replace("*", "")

    # Generate graph image (this is the answer)
    x = numpy.linspace(-15, 15, 400)
    y = sp.lambdify(sp.symbols('x'), equation, 'numpy')(x)

    fig, ax = plt.subplots(figsize=(6, 5), facecolor='none')
    ax.plot(x, y, color='black')
    ax.axhline(y=0, color='black', linewidth=0.5)  # x-axis
    ax.axvline(x=0, color='black', linewidth=0.5)  # y-axis

    # Mark intercepts
    ax.plot(0, sp.lambdify(sp.symbols('x'), equation, 'numpy')(0), 'ro',
            markersize=8)  # Y-intercept
    ax.plot(intercepts[0], 0, 'bo', markersize=8)  # X-intercept 1
    ax.plot(intercepts[1], 0, 'bo', markersize=8)  # X-intercept 2

    plt.axis('off')
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    plt.close(fig)
    buf.seek(0)

    image = QImage()
    image.loadFromData(buf.read())
    pixmap_answer = QPixmap.fromImage(image)  # The graph is the answer

    return difficulty, equation_text, pixmap_answer  # Return pixmap as answer
