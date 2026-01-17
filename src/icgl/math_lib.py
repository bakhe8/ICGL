"""
Utility library for calculating Fibonacci numbers.
"""
def fibonacci(n):
    """Calculates the nth Fibonacci number using an iterative approach."""
    if not isinstance(n, int) or n < 0:
        raise ValueError('Input must be a non-negative integer')
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
