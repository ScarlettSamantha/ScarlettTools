import os
import sys
import inspect

from importlib import import_module

MAGIC_PROPERTY_METHOD = 'METHOD'

if __name__ == "__main__":
    if sys.argv.__len__() <= 1:
        print("Build more parameters")
        exit(1)

    class_ = getattr(import_module("commands.%s" % sys.argv[1].lower()), sys.argv[1].lower().title())(*sys.argv[2:])
    if hasattr(class_, MAGIC_PROPERTY_METHOD):
        method_ = getattr(class_, getattr(class_, MAGIC_PROPERTY_METHOD))
        args_ = ([] if sys.argv.__len__() <= 3 else sys.argv[2:])
        send_args = False
    else:
        args_ = ([] if sys.argv.__len__() <= 3 else sys.argv[3:])
        method_ = getattr(class_, sys.argv[2])
    send_args = True

    if inspect.isgeneratorfunction(method_):
        for i in method_(*args_):
            print(i)
    else:
        if send_args:
            r = method_(*args_)
        else:
            r = method_()
        if r is not None:
            print(r)
