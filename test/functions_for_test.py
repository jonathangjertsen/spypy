






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


def function_with_args(x, y=1, *, z=3):
    return x + y + z








def function_that_raises_exception():
    raise ValueError("Error!")
