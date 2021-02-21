__all__ = ("ADT", "ADTMeta", "adt", "fieldmethod", "is_adt", "is_adt_field")

import functools
import re
import types
from typing import Callable, Tuple, Type, TypeVar


class _FieldMeta(type):
    def __new__(mcs, name, bases, namespace):
        return super().__new__(mcs, name, bases, namespace)

    def __instancecheck__(self, instance):
        return super().__instancecheck__(instance)


class _FieldBase(metaclass=_FieldMeta):

    __arg_types__: Tuple
    __adtbase__: "ADTMeta"

    def __init__(self, *args):
        if not hasattr(self, "__arg_types__"):
            raise TypeError("Cannot instantiate base field class")
        if len(args) != len(self.__arg_types__):
            raise TypeError(
                "Expected {} arg(s) for {!r} field, got {}".format(
                    len(self.__arg_types__), type(self).__name__, len(args)
                )
            )
        for f, t in zip(args, self.__arg_types__):
            if not (f is t is None) and type(t) is not TypeVar and not isinstance(f, t):
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
        if not (isinstance(other, type(self)) or isinstance(self, type(other))):
            return False
        return all(x == y for x, y in zip(iter(self), iter(other)))


def _make_field(name: str, field_base_cls: Type, arg_types: Tuple):
    field_cls = types.new_class(name, (field_base_cls,))
    field_cls.__module__ = field_base_cls.__module__
    field_cls.__arg_types__ = arg_types
    return field_cls


class ADTMeta(type):
    def __new__(mcs, name, bases, namespace):
        fieldmethods = {}
        generic_types = {}
        for attr_name, obj in list(namespace.items()):
            if getattr(obj, "__isfieldmethod__", False):
                namespace.pop(attr_name)
                fieldmethods[attr_name] = obj
            elif isinstance(obj, TypeVar):
                generic_types[attr_name] = obj

        namespace = dict(namespace)
        annotations = namespace.pop("__annotations__", {})
        field_base_cls = types.new_class("_FieldBase", (_FieldBase,))
        field_base_cls.__module__ = namespace["__module__"]
        field_base_cls.__name__ = "Field"  # TODO: remove
        fields = {}

        # Make the ADT base class.
        def __new__(cls, *args, **kwargs):
            raise TypeError(f"Cannot instantiate ADT class {cls.__name__!r}")

        namespace.update(
            {
                "__new__": __new__,
                "_fields": fields,
                "_generic_types": generic_types,
                "_FieldBase": field_base_cls,
                "Field": field_base_cls,  # TODO: remove
            }
        )
        cls = super().__new__(mcs, name, bases, namespace)
        if generic_types:
            cls.__qualname__ += "[{}]".format(
                ",".join(t.__name__ for t in generic_types.values())
            )
        field_base_cls.__adtbase__ = cls
        field_base_cls.__qualname__ = cls.__qualname__ + "." + field_base_cls.__name__

        # Make the field classes based on the ADT class annotations.
        for field_name, arg_types in annotations.items():
            if type(arg_types) is not tuple:
                raise TypeError(
                    f"{field_name!r} is a badly declared field - should use a tuple of types"
                )
            f = _make_field(field_name, field_base_cls, arg_types)
            f.__qualname__ = cls.__qualname__ + "." + f.__name__
            for method_name, method in fieldmethods.items():
                setattr(f, method_name, _fieldmethod(method, cls, f))
            fields[field_name] = f
            setattr(cls, field_name, f)

        return cls

    def __contains__(cls, item):
        return item in cls._fields.values() or type(item) in cls._fields.values()

    @functools.lru_cache()
    def __getitem__(cls, items):
        """Create subclass of given class with generics filled in."""
        if not isinstance(items, tuple):
            items = (items,)
        if len(items) != len(cls._generic_types):
            raise TypeError(f"Expected exactly {len(items)} generic types")

        namespace = cls.__dict__.copy()
        base_qualname = re.sub(r"(\[.*\])", "", cls.__qualname__)
        item_names = "[{}]".format(",".join(x.__name__ for x in items))
        namespace["__qualname__"] = f"{base_qualname}{item_names}"

        # Get mapping of typevars to concrete types.
        typevar_mapping = {}
        for (generic, typevar), typ in zip(namespace["_generic_types"].items(), items):
            namespace[generic] = typ
            namespace["_generic_types"][generic] = typ
            typevar_mapping[typevar] = typ

        # Subclass generic fields to concrete fields.
        new_base_field_cls = type(cls.Field)(
            "Field",
            (cls.Field,),
            {
                "__module__": cls.Field.__module__,
                "__qualname__": f"{namespace['__qualname__']}.Field",
            },
        )
        namespace["Field"] = new_base_field_cls
        new_fields = {}
        for field_name, field_cls in namespace["_fields"].items():
            __arg_types__ = tuple(
                typevar_mapping.get(t, t) for t in field_cls.__arg_types__
            )
            new_field_cls = type(field_cls)(
                field_name,
                (
                    new_base_field_cls,
                    field_cls,
                ),
                {
                    "__module__": field_cls.__module__,
                    "__qualname__": f"{namespace['__qualname__']}.{field_name}",
                    "__arg_types__": __arg_types__,
                },
            )
            new_fields[field_name] = new_field_cls
            namespace[field_name] = new_field_cls
        namespace["_fields"] = new_fields

        new_cls = super().__new__(type(cls), cls.__name__, (cls,), namespace)
        new_cls.Field.__adtbase__ = new_cls
        for f in new_cls._fields.values():
            f.__adtbase__ = cls
        return new_cls


class ADT(metaclass=ADTMeta):
    pass


def adt(_cls=None) -> ADTMeta:
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
        return obj in base_adt_cls
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
