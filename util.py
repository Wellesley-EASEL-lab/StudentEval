import numpy as np

# Source: Chen at al. Evaluating Large Language Models of Code. 2021
def passk(n: int, c: int, k: int) -> float:
    """
    Calculates 1 - comb(n - c, k) / comb(n, k).
    """
    assert c <= n, "c must be less than n"
    #if c != n and c > 0: 
    #    assert False, "c must be less than or equal to n"
    if n - c < k:
        return 1.0
    return 1.0 - np.prod(1.0 - k / np.arange(n - c + 1, n + 1))
