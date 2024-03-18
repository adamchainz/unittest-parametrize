from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest import TestResult
from unittest import mock

import pytest

from unittest_parametrize import ParametrizedTestCase
from unittest_parametrize import param
from unittest_parametrize import parametrize


def run_tests(test_case: type[ParametrizedTestCase]) -> TestResult:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(test_case)
    return unittest.TextTestRunner().run(suite)


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
            [{"x": 1}],  # type: ignore[arg-type]
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


def test_duplicate_param_ids():
    with pytest.raises(ValueError) as excinfo:
        parametrize(
            "x",
            [
                param(1, id="a"),
                param(1, id="a"),
            ],
        )

    assert excinfo.value.args[0] == "Duplicate param id 'a'"


def test_duplicate_param_ids_mixed():
    with pytest.raises(ValueError) as excinfo:
        parametrize(
            "x",
            [
                param(1),
                param(1, id="a"),
            ],
            ids=["a", None],
        )

    assert excinfo.value.args[0] == "Duplicate param id 'a'"


def test_duplicate_test_name():
    with pytest.raises(ValueError) as excinfo:

        class VanillaTest(ParametrizedTestCase):
            @parametrize(
                "x",
                [(1,)],
            )
            def test_something(self, x):  # pragma: no cover
                pass

            def test_something_0(self):  # pragma: no cover
                pass

    assert (
        excinfo.value.args[0] == "Duplicate test name test_something_0 in VanillaTest"
    )


def test_no_decorators_above_parametrize():
    obj = SimpleNamespace(x=1)

    with pytest.raises(TypeError) as excinfo:

        class SomethingTests(ParametrizedTestCase):
            @mock.patch.object(obj, "x", new=2)
            @parametrize(
                "y",
                [(1,)],
            )
            def test_something(self, y):  # pragma: no cover
                pass

    assert (
        excinfo.value.args[0]
        == "@parametrize must be the top-most decorator on"
        + " test_no_decorators_above_parametrize.<locals>.SomethingTests.test_something"
    )


def test_only_one_parametrize():
    with pytest.raises(TypeError) as excinfo:

        class SomethingTests(ParametrizedTestCase):
            @parametrize("x", [(1,)])
            @parametrize("y", [(2,)])
            def test_something(self, x, y):  # pragma: no cover
                pass

    assert (
        excinfo.value.args[0]
        == "@parametrize cannot be stacked on"
        + " test_only_one_parametrize.<locals>.SomethingTests.test_something"
    )


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


def test_argnames_whitespace():
    ran = 0

    class SquareTests(ParametrizedTestCase):
        @parametrize(
            "x, expected",
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


def test_param_instance_with_ids_arg():
    ran = 0

    class SquareTests(ParametrizedTestCase):
        @parametrize(
            "x,expected",
            [
                param(1, 1),
            ],
            ids=["one"],
        )
        def test_square(self, x: int, expected: int) -> None:
            nonlocal ran
            ran += 1
            self.assertEqual(x**2, expected)

    run_tests(SquareTests)

    assert ran == 1
    assert not hasattr(SquareTests, "test_square")
    assert hasattr(SquareTests, "test_square_one")


def test_param_instances_without_id():
    ran = 0

    class SquareTests(ParametrizedTestCase):
        @parametrize(
            "x,expected",
            [
                param(1, 1),
                param(20, 400, id="large"),
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
    assert hasattr(SquareTests, "test_square_large")


def test_param_instances_reused():
    ran = 0
    cases = [param(1, 1)]

    class SquareTests(ParametrizedTestCase):
        @parametrize("x,expected", cases)
        def test_square(self, x: int, expected: int) -> None:
            nonlocal ran
            ran += 1
            self.assertEqual(x**2, expected)

        @parametrize("x,expected", cases, ids=["minusone"])
        def test_negative_square(self, x: int, expected: int) -> None:
            nonlocal ran
            ran += 1
            self.assertEqual((-x) ** 2, expected)

    run_tests(SquareTests)

    assert ran == 2
    assert not hasattr(SquareTests, "test_square")
    assert hasattr(SquareTests, "test_square_0")
    assert hasattr(SquareTests, "test_negative_square_minusone")


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


def test_assertion_raised_with_param_info():
    expected_msg = "test_square failed with params: {'x': 1, 'expected': 2}"

    class SquareTests(ParametrizedTestCase):
        @parametrize("x,expected", ((1, 2),))
        def test_square(self, x: int, expected: int) -> None:
            self.assertEqual(x, expected)

    test_result = run_tests(SquareTests)

    assert len(test_result.failures) == 1

    (_, failure_msg) = test_result.failures[0]
    assert expected_msg in failure_msg
