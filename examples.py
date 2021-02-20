__all__ = ("Option", "Result")

from typing import Callable

import adt


class Option(metaclass=adt.ADTMeta):
    Some: (object,)
    Empty: ()

    @adt.fieldmethod
    def map(field, basecls, func: Callable):
        if type(field) is basecls.Some:
            return basecls.Some(func(field[0]))
        else:
            return field

    @adt.fieldmethod
    def and_then(field, basecls, func: Callable):
        if type(field) is basecls.Some:
            return func(field[0])
        else:
            return field

    @adt.fieldmethod
    def with_default(field, basecls, default):
        if type(field) is basecls.Some:
            return field
        else:
            return basecls.Some(default)


class Result(metaclass=adt.ADTMeta):
    Ok: (object,)
    Error: (object,)

    @adt.fieldmethod
    def map(field, basecls, func: Callable):
        if type(field) is basecls.Ok:
            return basecls.Ok(func(field[0]))
        else:
            return field

    @adt.fieldmethod
    def map_error(field, basecls, func: Callable):
        if type(field) is basecls.Ok:
            return field
        else:
            return basecls.Error(func(field[0]))

    @adt.fieldmethod
    def and_then(field, basecls, func: Callable):
        if type(field) is basecls.Ok:
            return func(field[0])
        else:
            return field

    @adt.fieldmethod
    def with_default(field, basecls, default):
        if type(field) is basecls.Ok:
            return field
        else:
            return basecls.Ok(default)

    @adt.fieldmethod
    def to_option(field, basecls):
        if type(field) is basecls.Ok:
            return Option.Some(field[0])
        else:
            return Option.Empty()

    @classmethod
    def from_option(cls, option, error):
        if type(option) is Option.Some:
            return cls.Ok(option[0])
        else:
            return cls.Error(error)
