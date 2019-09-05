








def trivial_function():
    a = 1
    b = 2
    c = a + b
    return c





def nontrivial_function():
    def closure(a):
        return math.sqrt(a)
    import math
    a = pow(2, 4)
    return closure(a)

