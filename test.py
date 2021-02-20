import dataclasses
from typing import Optional, Tuple

import pytest

import adt
from examples import Option, Result

# ------------------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------------------


@pytest.fixture
def MyADT():
    class _MyADT:
        foo: ()
        bar: (int,)
        baz: (int, bool, str, None)

    return adt.adt(_MyADT)


# ------------------------------------------------------------------------------
# Positive testcases
# ------------------------------------------------------------------------------


def test_create_with_decorator():
    @adt.adt
    class MyADT:
        foo: ()
        bar: (int,)
        baz: (int, bool, str, None)


def test_create_with_metaclass():
    class MyADT(metaclass=adt.ADTMeta):
        foo: ()
        bar: (int,)
        baz: (int, bool, str, None)


def test_is_adt(MyADT):
    assert type(MyADT) is adt.ADTMeta
    assert adt.is_adt(MyADT)
    assert not adt.is_adt(None)
    assert not adt.is_adt(MyADT.foo())


def test_is_adt_field(MyADT):
    assert isinstance(MyADT.foo(), MyADT.field_base_class)
    assert MyADT.field_base_class.__name__ == "_MyADTField"
    assert adt.is_adt_field(MyADT.foo)
    assert adt.is_adt_field(MyADT.foo())
    assert not adt.is_adt_field(None)
    assert not adt.is_adt_field(MyADT)


def test_adt_class_repr(MyADT):
    assert repr(MyADT) == f"<class '{__name__}._MyADT'>"


@pytest.mark.xfail(reason="TODO")
def test_field_class_repr(MyADT):
    assert repr(MyADT.foo) == f"<class '{__name__}._MyADT.foo'>"
    assert repr(MyADT.bar) == f"<class '{__name__}._MyADT.bar'>"


def test_field_inst_repr(MyADT):
    assert repr(MyADT.foo()) == "_MyADT.foo()"
    assert repr(MyADT.bar(1)) == "_MyADT.bar(1)"
    assert repr(MyADT.baz(1, False, "hi", None)) == "_MyADT.baz(1, False, 'hi', None)"


def test_is_field(MyADT):
    assert not MyADT.is_field(MyADT)
    assert MyADT.is_field(MyADT.bar)
    assert MyADT.is_field(MyADT.bar(1))


def test_adt_contains(MyADT):
    assert MyADT not in MyADT
    assert MyADT.bar in MyADT
    assert MyADT.bar(1) in MyADT


def test_equals(MyADT):
    assert MyADT.foo() == MyADT.foo()
    assert MyADT.bar(1) == MyADT.bar(1)
    assert MyADT.baz(1, False, "hi", None) == MyADT.baz(1, False, "hi", None)
    assert MyADT.bar(1) != MyADT.bar(2)


def test_iter(MyADT):
    assert list(MyADT.foo()) == []
    assert list(MyADT.bar(1)) == [1]
    assert list(MyADT.baz(1, False, "hi", None)) == [1, False, "hi", None]


def test_unpack(MyADT):
    (*no_elems,) = MyADT.foo()
    assert no_elems == []
    (bar_elem,) = MyADT.bar(1)
    assert bar_elem == 1
    baz_int, baz_bool, *baz_rest = MyADT.baz(1, False, "hi", None)
    assert baz_int == 1
    assert baz_bool is False
    assert baz_rest == ["hi", None]


def test_getitem(MyADT):
    assert MyADT.bar(1)[0] == 1
    baz = MyADT.baz(1, False, "hi", None)
    assert baz[0] == 1
    assert baz[1] is False
    assert baz[2:] == ("hi", None)


@pytest.mark.xfail(reason="TODO")
def test_typing_field():
    class _MyADT(metaclass=adt.ADTMeta):
        field: (Optional[str],)

    _MyADT.field("hi")
    _MyADT.field(None)


# ------------------------------------------------------------------------------
# Negative testcases
# ------------------------------------------------------------------------------


def test_create_bad_field_annotation():
    with pytest.raises(TypeError):

        class _MyADT(metaclass=adt.ADTMeta):
            field: Tuple[str]


def test_bad_field_type(MyADT):
    with pytest.raises(TypeError):
        MyADT.bar(None)
    with pytest.raises(TypeError):
        MyADT.baz(None, None, None, None)


def test_extra_field_value(MyADT):
    with pytest.raises(TypeError):
        MyADT.foo(1)
    with pytest.raises(TypeError):
        MyADT.bar(1, 2)


def test_missing_field_value(MyADT):
    with pytest.raises(TypeError):
        MyADT.bar()
    with pytest.raises(TypeError):
        MyADT.baz(1, False)


# ------------------------------------------------------------------------------
# Example usage
# ------------------------------------------------------------------------------


def test_minesweeper_cells():
    class CellContents(metaclass=adt.ADTMeta):
        Unclicked: ()
        Num: (int,)
        Flag: (int,)
        WrongFlag: (int,)
        Mine: (int,)
        HitMine: (int,)

        # TODO: Support __init_field__(cls, field) classmethod for validation?

        @classmethod
        def mine_count(cls, field) -> int:
            if type(field) in [cls.Flag, cls.Mine, cls.HitMine]:
                (value,) = field
                return value
            else:
                return 0

        @classmethod
        def is_immutable(cls, field) -> bool:
            return type(field) not in [cls.Unclicked, cls.Flag]

        @classmethod
        def increment_flag(cls, field):
            if type(field) is not cls.Flag:
                raise TypeError(f"Can only increment flag fields, got {field}")
            (value,) = field
            return type(field)(value + 1)

    unclicked = CellContents.Unclicked()
    space = CellContents.Num(0)
    num1 = CellContents.Num(1)
    num5 = CellContents.Num(5)
    flag1 = CellContents.Flag(1)
    flag2 = CellContents.Flag(2)

    assert CellContents.mine_count(unclicked) == 0
    assert CellContents.mine_count(num1) == 0
    assert CellContents.mine_count(flag2) == 2

    assert CellContents.is_immutable(num1)
    assert not CellContents.is_immutable(unclicked)

    assert CellContents.increment_flag(flag1) == flag2


def test_rust_example():
    # See https://doc.rust-lang.org/book/ch18-03-pattern-syntax.html#destructuring-enums
    #
    # Note: A dataclass is used in place of a Rust struct, but in reality this
    # is clunky and not recommended. There should be no need for combining
    # dataclasses with ADTs in this way (although we may want to allow named
    # ADT field params).

    @dataclasses.dataclass
    class _Move:
        x: int
        y: int

    class Message(metaclass=adt.ADTMeta):
        Quit: ()
        Move: (_Move,)  # TODO: Support string type annotations for reusing 'Move' name
        Write: (str,)
        ChangeColor: (int, int, int)

    def handle_msg(msg):
        if type(msg) is Message.Quit:
            return "The Quit variant has no data to destructure."
        elif type(msg) is Message.Move:
            x, y = dataclasses.astuple(msg[0])
            return f"Move in the x direction {x} and in the y direction {y}"
        elif type(msg) is Message.Write:
            return f"Text message: {msg[0]}"
        elif type(msg) is Message.ChangeColor:
            r, g, b = msg
            return f"Change the color to red {r}, green {g}, and blue {b}"
        assert False

    assert "Quit" in handle_msg(Message.Quit())
    assert handle_msg(Message.Move(_Move(x=1, y=2))) == (
        "Move in the x direction 1 and in the y direction 2"
    )
    assert handle_msg(Message.Write("hello!")) == "Text message: hello!"
    assert handle_msg(Message.ChangeColor(0, 160, 255)) == (
        "Change the color to red 0, green 160, and blue 255"
    )


# TODO: Implement generics (implement ADTMeta.__getitem__() to return subclass).


@pytest.mark.skip("TODO: testing of methods")
def test_option_type():
    Option.Some(1)
    Option.Empty()


def test_result_type():
    def do_something(value) -> "ResultField":
        if value >= 0:
            return Result.Ok(value >= 100)
        else:
            return Result.Error("Negative value")

    ok = Result.Ok(1)
    error = Result.Error("err")
    assert Result.Ok(1).and_then(do_something) == Result.Ok(False)
    assert Result.Ok(100).and_then(do_something) == Result.Ok(True)
    assert Result.Ok(-1).and_then(do_something) == Result.Error("Negative value")
    assert error.and_then(do_something) == Result.Error("err")
