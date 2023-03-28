from __future__ import annotations

import unittest

import pytest

from unittest_parametrize import param
from unittest_parametrize import parametrize
from unittest_parametrize import ParametrizedTestCase


def run_tests(test_case: type[ParametrizedTestCase]) -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(test_case)
    unittest.TextTestRunner().run(suite)


def test_wrong_length_argnames():
    with pytest.raises(ValueError) as excinfo:
        parametrize((), [])

    assert excinfo.value.args[0] == "argnames must contain at least one element"


def test_wrong_length_ids():
    with pytest.raises(ValueError) as excinfo:
        parametrize(
            "x",
            [(1,)],
            ids=[],
        )

    assert excinfo.value.args[0] == "ids must have the same length as argvalues"


def test_wrong_length_tuple():
    with pytest.raises(ValueError) as excinfo:
        parametrize(
            "x",
            [(2, 3)],
        )

    assert (
        excinfo.value.args[0]
        == "tuple at index 0 has wrong number of arguments (2 != 1)"
    )


def test_wrong_length_param():
    with pytest.raises(ValueError) as excinfo:
        parametrize(
            "x",
            [param(id="one")],
        )

    assert (
        excinfo.value.args[0]
        == "param at index 0 has wrong number of arguments (0 != 1)"
    )


def test_wrong_type_argvalues():
    with pytest.raises(TypeError) as excinfo:
        parametrize(
            "x",
            [{"x": 1}],  # type: ignore[list-item]
        )

    assert (
        excinfo.value.args[0]
        == "argvalue at index 0 is not a tuple or param instance: {'x': 1}"
    )


def test_wrong_argname():
    with pytest.raises(TypeError) as excinfo:

        @parametrize(
            "x",
            [(1,)],
        )
        def test_something(self, y):  # pragma: no cover
            pass

    assert excinfo.value.args[0] == "got an unexpected keyword argument 'x'"


def test_param_invalid_id():
    with pytest.raises(ValueError) as excinfo:
        param(id="!")

    assert excinfo.value.args[0] == "id must be a valid Python identifier suffix: '!'"


def test_vanilla():
    # Non-parametrized tests work as usual
    ran = False

    class VanillaTest(ParametrizedTestCase):
        def test_vanilla(self):
            nonlocal ran
            ran = True
            self.assertEqual(1, 1)

    run_tests(VanillaTest)

    assert ran


def test_simple_parametrized():
    ran = 0

    class SquareTests(ParametrizedTestCase):
        @parametrize(
            "x,expected",
            [
                (1, 1),
                (2, 4),
            ],
        )
        def test_square(self, x: int, expected: int) -> None:
            nonlocal ran
            ran += 1
            self.assertEqual(x**2, expected)

    run_tests(SquareTests)

    assert ran == 2
    assert not hasattr(SquareTests, "test_square")
    assert hasattr(SquareTests, "test_square_0")
    assert hasattr(SquareTests, "test_square_1")


def test_full_argnames():
    ran = 0

    class SquareTests(ParametrizedTestCase):
        @parametrize(
            ("x", "expected"),
            [
                (1, 1),
                (2, 4),
            ],
        )
        def test_square(self, x: int, expected: int) -> None:
            nonlocal ran
            ran += 1
            self.assertEqual(x**2, expected)

    run_tests(SquareTests)

    assert ran == 2
    assert not hasattr(SquareTests, "test_square")
    assert hasattr(SquareTests, "test_square_0")
    assert hasattr(SquareTests, "test_square_1")


def test_custom_ids():
    ran = 0

    class SquareTests(ParametrizedTestCase):
        @parametrize(
            "x,expected",
            [
                (1, 1),
                (2, 4),
            ],
            ids=["one", "two"],
        )
        def test_square(self, x: int, expected: int) -> None:
            nonlocal ran
            ran += 1
            self.assertEqual(x**2, expected)

    run_tests(SquareTests)

    assert ran == 2
    assert not hasattr(SquareTests, "test_square")
    assert hasattr(SquareTests, "test_square_one")
    assert hasattr(SquareTests, "test_square_two")


def test_param_instances():
    ran = 0

    class SquareTests(ParametrizedTestCase):
        @parametrize(
            "x,expected",
            [
                param(1, 1, id="one"),
                param(2, 4, id="two"),
            ],
        )
        def test_square(self, x: int, expected: int) -> None:
            nonlocal ran
            ran += 1
            self.assertEqual(x**2, expected)

    run_tests(SquareTests)

    assert ran == 2
    assert not hasattr(SquareTests, "test_square")
    assert hasattr(SquareTests, "test_square_one")
    assert hasattr(SquareTests, "test_square_two")


def test_zero_parametrized():
    # Zero parametrized tests allowed to make generating tests easier

    ran = False

    class NoTests(ParametrizedTestCase):
        @parametrize("x", [])
        def test_never_runs(self, x: int) -> None:  # pragma: no cover
            nonlocal ran
            ran = True

    run_tests(NoTests)

    assert ran is False
    assert not hasattr(NoTests, "test_never_runs")
    assert not hasattr(NoTests, "test_never_runs_0")
