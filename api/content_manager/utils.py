from typing import get_args


# TODO: Can eventually be swapped out for `typing.get_original_bases` in CPython 3.12.
def get_bases(cls):
    try:
        return cls.__orig_bases__
    except AttributeError:
        try:
            return cls.__bases__
        except AttributeError:
            raise TypeError(f"Excepted an instance of type, not {type(cls).__name__!r}")


def get_derived_type(cls):
    t = get_bases(cls)[0]
    return get_args(t)[0]
