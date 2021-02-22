# Algebraic Data Types in Python

```python
import adt

class MyADT(adt.ADT):
    foo: ()
    bar: (int,)
    baz: (int, bool, str, None)

    @adt.fieldmethod
    def double_first(field, basecls) -> "MyADT":
        if isinstance(field, basecls.foo):
            raise TypeError(
                f"{basecls.foo.__qualname__} does not support doubling"
            )
        field_type = type(field)
        first, *rem = field
        return field_type(first * 2, *rem)

foo = MyADT.foo()
bar = MyADT.bar(4)
baz = MyADT.baz(3, False, "hi", None)

for val in [foo, bar, baz]:
    print(val)
    try:
        doubled = val.double_first()
        print("Doubled:", doubled)
    except TypeError:
        print("Failed to double")
    print()
```

See `examples/`, `adt/example.py` and `tests/test.py`.
