__all__ = ("ADT", "ADTMeta", "adt", "fieldmethod", "is_adt", "is_adt_field")

import functools
from typing import Callable, Tuple, Type


def _make_field(adt_cls_name: str, field_base_cls: Type, name: str, typ: Tuple):
    def __init__(self, *args):
        if len(args) != len(typ):
            raise TypeError(
                f"Expected {len(typ)} arg(s) for {name!r} field, got {len(args)}"
            )
        for f, t in zip(args, typ):
            if not (f is t is None) and not isinstance(f, t):
                raise TypeError(
                    f"Expected instance of type {t.__name__!r}, got {type(f).__name__!r}"
                )
        self._args = args

    def __repr__(self):
        return (
            f"{self.__class__.__qualname__}({', '.join(repr(x) for x in self._args)})"
        )

    def __iter__(self):
        return iter(self._args)

    def __getitem__(self, idx):
        return self._args[idx]

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return all(x == y for x, y in zip(iter(self), iter(other)))

    field_cls = type(
        name,
        (field_base_cls,),
        {
            "__qualname__": f"{adt_cls_name}.{name}",
            "__init__": __init__,
            "__repr__": __repr__,
            "__iter__": __iter__,
            "__getitem__": __getitem__,
            "__eq__": __eq__,
        },
    )

    return field_cls


class ADTMeta(type):
    def __new__(mcs, name, bases, namespace):
        # First make the field classes based on the ADT class annotations.
        annotations = namespace.get("__annotations__", {})
        field_base_cls = type(f"{name}Field", (), {})
        fields = {}
        for f, typ in annotations.items():
            if type(typ) is not tuple:
                raise TypeError(
                    f"{f!r} is a badly declared field - should use a tuple of types"
                )
            fields[f] = _make_field(name, field_base_cls, f, typ)

        # Now make the ADT base class itself.
        def __new__(cls, *args, **kwargs):
            raise TypeError(f"Cannot instantiate ADT class {cls.__name__!r}")

        @classmethod
        def is_field(cls, item) -> bool:
            return isinstance(item, cls.field_base_class) or (
                isinstance(item, type) and issubclass(item, cls.field_base_class)
            )

        fieldmethods = {}
        for attr_name, obj in list(namespace.items()):
            if getattr(obj, "__isfieldmethod__", False):
                namespace.pop(attr_name)
                fieldmethods[attr_name] = obj

        namespace = {
            "_fields": fields,
            "field_base_class": field_base_cls,
            "is_field": is_field,
            **fields,
            **namespace,
            "__new__": __new__,  # Last to override possible namespace entry
        }

        cls = super().__new__(mcs, name, bases, namespace)

        # Finally link aspects of the base class into the fields.
        for f in fields.values():
            f.__adtbase__ = cls
            f.__module__ = cls.__module__
            for method_name, method in fieldmethods.items():
                setattr(f, method_name, _fieldmethod(method, cls, f))

        return cls

    def __contains__(cls, item):
        return cls.is_field(item)


class ADT(metaclass=ADTMeta):
    pass


def adt(_cls=None):
    """
    Make a class into an ADT (Algebraic Data Type).

    Inspired by dataclasses.

    No support for:
     - Inheritance

    Notes:
     - Annotations are used, but there's no inherent reason to do so.
    """

    def wrap(cls):
        return ADTMeta(cls.__name__, (), cls.__dict__)

    # See if we're being called as @adt or @adt().
    if _cls is None:
        # We're called with parens.
        return wrap

    # We're called as @adt without parens.
    return wrap(_cls)


def is_adt(obj) -> bool:
    return isinstance(obj, ADTMeta)


def is_adt_field(obj) -> bool:
    base_adt_cls = getattr(obj, "__adtbase__", None)
    if base_adt_cls:
        return base_adt_cls.is_field(obj)
    return False


class _fieldmethod:
    def __init__(self, func: Callable, adt_base_cls: Type, field_cls: Type):
        self.func = func
        self.adt_base_cls = adt_base_cls
        self.field_cls = field_cls

    def __get__(self, obj, objtype=None):
        @functools.wraps(self.func)
        def newfunc(*args, **kwargs):
            return self.func(obj, self.adt_base_cls, *args, **kwargs)

        return newfunc


def fieldmethod(funcobj):
    funcobj.__isfieldmethod__ = True
    return funcobj
