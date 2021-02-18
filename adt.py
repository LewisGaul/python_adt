from typing import Tuple, Type


# ------------------------------------------------------------------------------
# Implementation code
# ------------------------------------------------------------------------------

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
        return f"{self.__class__.__qualname__}({', '.join(repr(x) for x in self._args)})"

    def __iter__(self):
        return iter(self._args)

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
            "__eq__": __eq__,
        },
    )

    return field_cls


class ADTMeta(type):
    def __new__(mcs, name, bases, namespace):
        annotations = namespace.get("__annotations__", {})
        field_base_cls = type(f"{name}Field", (), {})
        fields = {}
        for f, typ in annotations.items():
            if type(typ) is not tuple:
                raise TypeError(
                    f"{f!r} is a badly declared field - should use a tuple of types"
                )
            fields[f] = _make_field(name, field_base_cls, f, typ)

        def __new__(cls, *args, **kwargs):
            raise TypeError(f"Cannot instantiate ADT class {cls.__name__!r}")

        @classmethod
        def is_field(cls, item) -> bool:
            return (
                isinstance(item, cls._field_base_class) or
                (isinstance(item, type) and issubclass(item, cls._field_base_class))
            )

        namespace = {
            "_fields": fields,
            "_field_base_class": field_base_cls,
            "is_field": is_field,
            **fields,
            **namespace,
            "__new__": __new__,
        }

        return super().__new__(mcs, name, bases, namespace)

    def __contains__(cls, item):
        return cls.is_field(item)


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



# ------------------------------------------------------------------------------
# User code
# ------------------------------------------------------------------------------

@adt
class MyADT:
    foo: ()
    bar: (int,)
    baz: (int, bool, str, None)


print()
print(MyADT)
print(type(MyADT))
print(MyADT.foo)

print()
print("field instances:")
print(MyADT.foo())
print(MyADT.bar(1))
print(MyADT.baz(1, False, "hi", None))

print()
print("is_field():")
print(MyADT.is_field(MyADT))
print(MyADT.is_field(MyADT.baz))
print(MyADT.is_field(MyADT.baz(1, False, "hi", None)))

print()
print("Class contains:")
print(MyADT in MyADT)
print(MyADT.baz in MyADT)
print(MyADT.baz(1, False, "hi", None) in MyADT)

print()
print("Equality:")
print(MyADT.foo() == MyADT.foo())
print(MyADT.bar(1) == MyADT.bar(1))
print(MyADT.bar(1) == MyADT.bar(2))
