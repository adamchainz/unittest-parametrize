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


def test_wrong_length_ids():
    with pytest.raises(ValueError) as excinfo:
        parametrize(
            ("x",),
            [(1,)],
            ids=[],
        )

    assert excinfo.value.args[0] == "ids must have the same length as argvalues"


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
            ("x", "expected"),
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
            ("x", "expected"),
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


def test_two_parametrized():
    # Two parametrized tests within one class

    ran = 0

    class HigherPowerTests(ParametrizedTestCase):
        @parametrize(
            ("x", "expected"),
            [
                (1, 1),
                (2, 8),
            ],
        )
        def test_cube(self, x: int, expected: int) -> None:
            nonlocal ran
            ran += 1
            result = x**3
            self.assertEqual(result, expected)

        @parametrize(
            ("x", "expected"),
            [
                (1, 1),
                (2, 16),
            ],
        )
        def test_biquadrate(self, x: int, expected: int) -> None:
            nonlocal ran
            ran += 1
            result = x**4
            self.assertEqual(result, expected)

    run_tests(HigherPowerTests)

    assert ran == 4
    assert not hasattr(HigherPowerTests, "test_cube")
    assert hasattr(HigherPowerTests, "test_cube_0")
    assert hasattr(HigherPowerTests, "test_cube_1")
    assert not hasattr(HigherPowerTests, "test_biquadrate")
    assert hasattr(HigherPowerTests, "test_biquadrate_0")
    assert hasattr(HigherPowerTests, "test_biquadrate_1")
