import dataclasses
from typing import Optional, Tuple, TypeVar

import pytest

import adt
from adt.examples import Option, Result


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


@pytest.fixture
def OtherADT():
    class _OtherADT:
        foo: ()
        bar: (int,)

    return adt.adt(_OtherADT)


@pytest.fixture
def GenericADT():
    class _GenericADT:
        T = TypeVar("T")
        U = TypeVar("U")

        foo: (T,)
        bar: (T, U)
        plain: (int,)

    return adt.adt(_GenericADT)


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


def test_create_generic(GenericADT):
    assert GenericADT[int, str] is GenericADT[int, str]
    assert GenericADT[int, str] != GenericADT[bool, str]
    assert GenericADT[int, str] != GenericADT
    assert GenericADT.foo(1) == GenericADT[int, GenericADT.U].foo(1)


def test_name_dunders(MyADT, GenericADT):
    assert MyADT.__name__ == "_MyADT"
    assert MyADT.__qualname__ == "_MyADT"
    assert MyADT._FieldBase.__name__ == "_FieldBase"
    assert MyADT._FieldBase.__qualname__ == "_MyADT._FieldBase"
    assert MyADT.foo.__name__ == "foo"
    assert MyADT.foo.__qualname__ == "_MyADT.foo"
    assert GenericADT.__name__ == "_GenericADT"
    assert GenericADT.__qualname__ == "_GenericADT[T,U]"
    assert GenericADT._FieldBase.__name__ == "_FieldBase"
    assert GenericADT._FieldBase.__qualname__ == "_GenericADT[T,U]._FieldBase"
    assert GenericADT.foo.__name__ == "foo"
    assert GenericADT.foo.__qualname__ == "_GenericADT[T,U].foo"
    assert GenericADT[int, str].__name__ == "_GenericADT"
    assert GenericADT[int, str].__qualname__ == "_GenericADT[int,str]"
    assert GenericADT[int, str]._FieldBase.__name__ == "_FieldBase"
    assert (
        GenericADT[int, str]._FieldBase.__qualname__
        == "_GenericADT[int,str]._FieldBase"
    )
    assert GenericADT[int, str].foo.__name__ == "foo"
    assert GenericADT[int, str].foo.__qualname__ == "_GenericADT[int,str].foo"


def test_adt_class_repr(MyADT, GenericADT):
    assert repr(MyADT) == f"<class '{__name__}._MyADT'>"
    assert repr(GenericADT) == f"<class '{__name__}._GenericADT[T,U]'>"
    assert repr(GenericADT[int, str]) == f"<class '{__name__}._GenericADT[int,str]'>"


def test_field_class_repr(MyADT, GenericADT):
    assert repr(MyADT._FieldBase) == f"<class '{__name__}._MyADT._FieldBase'>"
    assert repr(MyADT.foo) == f"<class '{__name__}._MyADT.foo'>"
    assert repr(MyADT.bar) == f"<class '{__name__}._MyADT.bar'>"
    assert (
        repr(GenericADT._FieldBase)
        == f"<class '{__name__}._GenericADT[T,U]._FieldBase'>"
    )
    assert repr(GenericADT.foo) == f"<class '{__name__}._GenericADT[T,U].foo'>"
    assert repr(GenericADT.bar) == f"<class '{__name__}._GenericADT[T,U].bar'>"
    assert (
        repr(GenericADT[int, str]._FieldBase)
        == f"<class '{__name__}._GenericADT[int,str]._FieldBase'>"
    )
    assert (
        repr(GenericADT[int, str].foo)
        == f"<class '{__name__}._GenericADT[int,str].foo'>"
    )
    assert (
        repr(GenericADT[int, str].bar)
        == f"<class '{__name__}._GenericADT[int,str].bar'>"
    )


def test_field_inst_repr(MyADT, GenericADT):
    assert repr(MyADT.foo()) == "_MyADT.foo()"
    assert repr(MyADT.bar(1)) == "_MyADT.bar(1)"
    assert repr(MyADT.baz(1, False, "hi", None)) == "_MyADT.baz(1, False, 'hi', None)"
    assert repr(GenericADT.foo(1)) == "_GenericADT[T,U].foo(1)"
    assert repr(GenericADT.bar(1, "hi")) == "_GenericADT[T,U].bar(1, 'hi')"
    assert repr(GenericADT.plain(1)) == "_GenericADT[T,U].plain(1)"
    assert repr(GenericADT[int, str].foo(1)) == "_GenericADT[int,str].foo(1)"
    assert (
        repr(GenericADT[int, str].bar(1, "hi")) == "_GenericADT[int,str].bar(1, 'hi')"
    )
    assert repr(GenericADT[int, str].plain(1)) == "_GenericADT[int,str].plain(1)"


def test_class_hierarchy(MyADT, GenericADT):
    assert type(MyADT) is adt.ADTMeta
    assert issubclass(MyADT._FieldBase, adt._FieldBase)
    assert issubclass(MyADT.foo, MyADT._FieldBase)
    assert isinstance(MyADT.foo(), MyADT._FieldBase)
    assert not issubclass(MyADT._FieldBase, MyADT)
    assert issubclass(MyADT.foo, MyADT)
    assert isinstance(MyADT.foo(), MyADT)

    assert type(GenericADT) is adt.ADTMeta
    assert issubclass(GenericADT.foo, GenericADT._FieldBase)
    assert issubclass(GenericADT[int, str], GenericADT)
    assert issubclass(GenericADT[int, str]._FieldBase, GenericADT._FieldBase)
    assert issubclass(GenericADT[int, str].foo, GenericADT[int, str]._FieldBase)
    assert isinstance(GenericADT[int, str].plain(1), GenericADT._FieldBase)
    assert issubclass(GenericADT[int, str].foo, GenericADT[int, str])
    assert isinstance(GenericADT[int, str].plain(1), GenericADT[int, str])
    assert issubclass(GenericADT[int, str].foo, GenericADT)
    assert isinstance(GenericADT[int, str].plain(1), GenericADT)
    assert not issubclass(GenericADT.foo, GenericADT[int, str])
    assert not isinstance(GenericADT.plain(1), GenericADT[int, str])


def test_is_adt(MyADT):
    assert adt.is_adt(MyADT)
    assert not adt.is_adt(None)
    assert not adt.is_adt(MyADT.foo())


def test_is_adt_field(MyADT):
    assert adt.is_adt_field(MyADT.foo)
    assert adt.is_adt_field(MyADT.foo())
    assert not adt.is_adt_field(None)
    assert not adt.is_adt_field(MyADT)


def test_adt_contains(MyADT):
    assert MyADT not in MyADT
    assert MyADT.bar in MyADT
    assert MyADT.bar(1) in MyADT


def test_equals(MyADT, OtherADT):
    assert MyADT.foo() == MyADT.foo()
    assert MyADT.bar(1) == MyADT.bar(1)
    assert MyADT.baz(1, False, "hi", None) == MyADT.baz(1, False, "hi", None)
    assert MyADT.bar(1) != MyADT.bar(2)
    assert MyADT.bar(1) != OtherADT.bar(1)


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


def test_field_getitem(MyADT):
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


def test_init_adt_base_class(MyADT):
    with pytest.raises(TypeError):
        MyADT()


def test_init_adt_field_base_class(MyADT):
    with pytest.raises(TypeError):
        MyADT._FieldBase()


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


def test_invalid_generic(GenericADT):
    with pytest.raises(TypeError):
        GenericADT[int]
    with pytest.raises(TypeError):
        GenericADT[int, int, int]


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

        @adt.fieldmethod
        def mine_count(field, basecls) -> int:
            if type(field) in [basecls.Flag, basecls.Mine, basecls.HitMine]:
                (value,) = field
                return value
            else:
                return 0

        @adt.fieldmethod
        def is_immutable(field, basecls) -> bool:
            return type(field) not in [basecls.Unclicked, basecls.Flag]

        @adt.fieldmethod
        def increment_flag(field, basecls) -> "CellContents":
            if type(field) is not basecls.Flag:
                raise TypeError(f"Can only increment flag fields, got {field}")
            (value,) = field
            return type(field)(value + 1)

    unclicked = CellContents.Unclicked()
    space = CellContents.Num(0)
    num1 = CellContents.Num(1)
    num5 = CellContents.Num(5)
    flag1 = CellContents.Flag(1)
    flag2 = CellContents.Flag(2)

    assert unclicked.mine_count() == 0
    assert num1.mine_count() == 0
    assert flag2.mine_count() == 2

    assert num1.is_immutable()
    assert not unclicked.is_immutable()

    assert flag1.increment_flag() == flag2
    with pytest.raises(TypeError):
        num1.increment_flag()


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
        Move: (
            _Move,
        )  # TODO: Support string type annotations for reusing 'Move' name (?)
        Write: (str,)
        ChangeColor: (int, int, int)

        @adt.fieldmethod
        def handle(field, basecls) -> str:
            if type(field) is Message.Quit:
                return "The Quit variant has no data to destructure."
            elif type(field) is Message.Move:
                x, y = dataclasses.astuple(field[0])
                return f"Move in the x direction {x} and in the y direction {y}"
            elif type(field) is Message.Write:
                return f"Text message: {field[0]}"
            elif type(field) is Message.ChangeColor:
                r, g, b = field
                return f"Change the color to red {r}, green {g}, and blue {b}"
            assert False

    assert "Quit" in Message.Quit().handle()
    assert Message.Move(_Move(x=1, y=2)).handle() == (
        "Move in the x direction 1 and in the y direction 2"
    )
    assert Message.Write("hello!").handle() == "Text message: hello!"
    assert Message.ChangeColor(0, 160, 255).handle() == (
        "Change the color to red 0, green 160, and blue 255"
    )


@pytest.mark.skip("TODO: testing of methods")
def test_option_type():
    Option.Some(1)
    Option.Empty()


def test_result_type():
    R_int = Result[int, str]
    R_bool = Result[bool, str]

    def do_something(value: int) -> R_bool:
        if value >= 0:
            return R_bool.Ok(value >= 100)
        else:
            return R_bool.Error("Negative value")

    ok = R_int.Ok(1)
    error = R_int.Error("err")
    assert ok.and_then(do_something) == R_bool.Ok(False)
    assert R_int.Ok(100).and_then(do_something) == R_bool.Ok(True)
    assert R_int.Ok(-1).and_then(do_something) == R_bool.Error("Negative value")
    assert error.and_then(do_something) == R_bool.Error("err")
    assert type(error.and_then(do_something)) is R_bool.Error
