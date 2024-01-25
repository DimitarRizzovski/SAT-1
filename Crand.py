import random


def non_zero_one_randint(a, b):
    """Generate a random integer between a and b, inclusive, but re-roll if it's zero or one."""
    result = 0
    while result == 0 or result == 1:
        result = random.randint(a, b)
    return result


def non_zero_randint(a, b):
    """Generate a random integer between a and b, inclusive, but re-roll if it's zero."""
    result = 0
    while result == 0:
        result = random.randint(a, b)
    return result


def rand_op(*args):
    """Choose a random operator from the provided arguments."""
    if len(args) == 0:
        raise ValueError("At least one argument is required")
    return random.choice(args)
