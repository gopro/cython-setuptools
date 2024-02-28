# cython: language_level=3

cdef extern from "foo.h":
    int foo()


def bar():
    print(foo())
