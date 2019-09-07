






# It is important for the test that this function starts on line 10
# And that the 'length' assigned to it is equal to the number of code lines
def trivial_function():
    a = 1
    b = 2
    c = a + b
    del b
    return c
trivial_function.start = 10
trivial_function.length = 5


def nontrivial_function():
    def closure(a):
        return math.sqrt(a)
    import math
    a = pow(2, 4)
    return closure(a)

