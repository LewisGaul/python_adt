__all__ = ("Option", "Result")

from typing import Callable, TypeVar, Union

import adt


class Option(metaclass=adt.ADTMeta):

    T = TypeVar("T")

    Some: (T,)
    Empty: ()

    @adt.fieldmethod
    def map(field, basecls, func: Callable[[T], "U"]) -> "Option[U]":
        # Convert to new option type.
        try:
            ok_type = func.__annotations__["return"]
            assert isinstance(ok_type, type)
            result_cls = basecls[ok_type]
        except Exception:
            result_cls = basecls

        if type(field) is basecls.Some:
            return result_cls.Some(func(field[0]))
        else:
            return result_cls.Nothing()

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

    T = TypeVar("T")
    E = TypeVar("E")

    Ok: (T,)
    Error: (E,)

    @adt.fieldmethod
    def map(field, basecls, func: Callable[[T], "U"]) -> "Result[U,E]":
        # Convert to new result type.
        try:
            ok_type = func.__annotations__["return"]
            assert isinstance(ok_type, type)
            result_cls = basecls[ok_type, basecls.E]
        except Exception:
            result_cls = basecls

        if type(field) is basecls.Ok:
            return result_cls.Ok(func(field[0]))
        else:
            return result_cls.Error(field[0])

    @adt.fieldmethod
    def map_error(field, basecls, func: Callable[[E], "F"]) -> "Result[T,F]":
        # Convert to new result type.
        try:
            err_type = func.__annotations__["return"]
            assert isinstance(err_type, type)
            result_cls = basecls[basecls.T, err_type]
        except Exception:
            result_cls = basecls

        if type(field) is basecls.Ok:
            return result_cls.Ok(field[0])
        else:
            return result_cls.Error(func(field[0]))

    @adt.fieldmethod
    def and_then(field, basecls, func: Callable[[T], "Result[U,E]"]) -> "Result[U,E]":
        # Convert to new result type.
        try:
            result_cls = func.__annotations__["return"]
        except Exception:
            result_cls = basecls

        if type(field) is basecls.Ok:
            return func(field[0])
        else:
            return result_cls.Error(field[0])

    @adt.fieldmethod
    def with_default(field, basecls, default: "U") -> Union[T, "U"]:
        if type(field) is basecls.Ok:
            return field[0]
        else:
            return default

    @adt.fieldmethod
    def to_option(field, basecls) -> Option[T]:
        if type(field) is basecls.Ok:
            return Option[basecls.T].Some(field[0])
        else:
            return Option[basecls.T].Empty()

    @classmethod
    def from_option(cls, option: Option[T], error: E) -> "Result[T,E]":
        if type(option) is Option.Some:
            return cls.Ok(option[0])
        else:
            return cls.Error(error)
