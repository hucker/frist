import pytest

from frist.units._base import Inclusive, coerce_inclusive


def test_coerce_inclusive_accepts_strings_and_enum():
    assert coerce_inclusive("both") is Inclusive.BOTH
    assert coerce_inclusive("left") is Inclusive.LEFT
    assert coerce_inclusive(Inclusive.RIGHT) is Inclusive.RIGHT


def test_coerce_inclusive_rejects_invalid():
    with pytest.raises(ValueError):
        coerce_inclusive("bogus")
