import random

import Crand
from sympy import symbols, solve, simplify, factor, expand
import sympy as sp


# For Quadratics Expansion
def expand(original_equation):
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
        expanded_equation = str(expanded_equation).replace("**","^").replace("*", "")
        original_equation_str = str(original_equation).replace("**","^").replace("*", "")
        return expanded_equation, original_equation_str  # Flip the order here
    def generate_equation_hard():
        x = sp.symbols('x')
        original_equation = f"({Crand.non_zero_randint(-5, 5)}*x {random.choice(['+', '-'])} {random.randint(1, 5)})*({Crand.non_zero_randint(-5, 5)}*x {random.choice(['+', '-'])} {random.randint(1, 5)})"
        expanded_equation = expand(original_equation)
        expanded_equation = str(expanded_equation).replace("**","^").replace("*", "")
        original_equation_str = str(original_equation).replace("**","^").replace("*", "")
        return expanded_equation, original_equation_str  # Flip the order here

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
        x1, x2 = random.randint(lower, upper), random.randint(lower, upper)
        answer = (x - x1) * (x - x2)
        return answer, (x1, x2)

    if difficulty == "Easy":
        equation, answer = generate_equation(1, 5)
    elif difficulty == "Medium":
        equation, answer = generate_equation(-5, 5)
    elif difficulty == "Hard":
        equation, answer = generate_equation(-10, 10)
    else:
        equation, answer = "Unknown difficulty", None

    equation_text = sp.expand(equation)

    return difficulty, equation_text, answer