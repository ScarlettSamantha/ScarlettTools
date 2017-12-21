import os
import sys
import inspect

from importlib import import_module

if __name__ == "__main__":
    if sys.argv.__len__() <= 1:
        print("Build more parameters")
        exit(1)

    args_ = ([] if sys.argv.__len__() <= 3 else sys.argv[3:])
    class_ = getattr(import_module("commands.%s" % sys.argv[1].lower()), sys.argv[1].lower().title())(*args_)
    method_ = getattr(class_, sys.argv[2])

    if inspect.isgeneratorfunction(method_):
        for i in method_(*args_):
            print(i)
    else:
        r = method_(*args_)
        if r is not None:
            print(r)

