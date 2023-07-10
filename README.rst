====================
unittest-parametrize
====================

.. image:: https://img.shields.io/github/actions/workflow/status/adamchainz/unittest-parametrize/main.yml?branch=main&style=for-the-badge
   :target: https://github.com/adamchainz/unittest-parametrize/actions?workflow=CI

.. image:: https://img.shields.io/pypi/v/unittest-parametrize.svg?style=for-the-badge
   :target: https://pypi.org/project/unittest-parametrize/

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge
   :target: https://github.com/psf/black

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=for-the-badge
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit

Parametrize tests within unittest TestCases.

Installation
============

Install with:

.. code-block:: bash

    python -m pip install unittest-parametrize

Python 3.8 to 3.12 supported.

----

**Testing a Django project?**
Check out my book `Speed Up Your Django Tests <https://adamchainz.gumroad.com/l/suydt>`__ which covers loads of recommendations to write faster, more accurate tests.

----

Usage
=====

The API mirrors |@pytest.mark.parametrize|__ as much as possible.
(Even the name `parametrize <https://en.wiktionary.org/wiki/parametrize#English>`__ over the slightly more common `parameterize <https://en.wiktionary.org/wiki/parameterize#English>`__ with an extra “e”.
Don’t get caught out by that…)

.. |@pytest.mark.parametrize| replace:: ``@pytest.mark.parametrize``
__ https://docs.pytest.org/en/stable/how-to/parametrize.html#parametrize-basics

There are two steps to parametrize a test case:

1. Use ``ParametrizedTestCase`` in the base classes for your test case.
2. Apply ``@parametrize`` to any tests for parametrization.
   This decorator takes (at least):

   * the argument names to parametrize, as comma-separated string
   * a list of parameter tuples to create individual tests for

Here’s a basic example:

.. code-block:: python

    from unittest_parametrize import parametrize
    from unittest_parametrize import ParametrizedTestCase


    class SquareTests(ParametrizedTestCase):
        @parametrize(
            "x,expected",
            [
                (1, 1),
                (2, 4),
            ],
        )
        def test_square(self, x: int, expected: int) -> None:
            self.assertEqual(x**2, expected)

``@parametrize`` modifies the class at definition time with Python’s |__init_subclass__ hook|__.
It removes the original test method and creates wrapped copies with individual names.
Thus the parametrization should work regardless of the test runner you use (be it unittest, Django’s test runner, pytest, etc.).

.. |__init_subclass__ hook| replace:: ``__init_subclass__`` hook
__ https://docs.python.org/3/reference/datamodel.html#object.__init_subclass__

Provide argument names as separate strings
------------------------------------------

You can provide argument names as a sequence of strings instead:

.. code-block:: python

    from unittest_parametrize import parametrize
    from unittest_parametrize import ParametrizedTestCase


    class SquareTests(ParametrizedTestCase):
        @parametrize(
            ("x", "expected"),
            [
                (1, 1),
                (2, 4),
            ],
        )
        def test_square(self, x: int, expected: int) -> None:
            self.assertEqual(x**2, expected)


Use ``ParametrizedTestCase`` in your base test case class
---------------------------------------------------------

``ParametrizedTestCase`` does nothing if there aren’t any ``@parametrize``-decorated tests within a class.
Therefore you can include it in your project’s base test case class so that ``@parametrize`` works immediately in all test cases.

For example, within a Django project, you can create a set of project-specific base test case classes extending `those provided by Django <https://docs.djangoproject.com/en/stable/topics/testing/tools/#provided-test-case-classes>`__.
You can do this in a module like ``example.test``, and use the base classes throughout your test suite.
To add ``ParametrizedTestCase`` to all your copies, use it in a custom ``SimpleTestCase`` and then mixin to others using multiple inheritance like so:

.. code-block:: python

    from django import test
    from unittest_parametrize import ParametrizedTestCase


    class SimpleTestCase(ParametrizedTestCase, test.SimpleTestCase):
        pass


    class TestCase(SimpleTestCase, test.TestCase):
        pass


    class TransactionTestCase(SimpleTestCase, test.TransactionTestCase):
        pass


    class LiveServerTestCase(SimpleTestCase, test.LiveServerTestCase):
        pass

Custom test name suffixes
-------------------------

By default, test names are extended with an index, starting at zero.
You can see these names when running the tests:

.. code-block:: console

    $ python -m unittest t.py -v
    test_square_0 (t.SquareTests.test_square_0) ... ok
    test_square_1 (t.SquareTests.test_square_1) ... ok

    ----------------------------------------------------------------------
    Ran 2 tests in 0.000s

    OK

You can customize these names by passing ``param`` objects, which contain the arguments and an optional ID for the suffix:

.. code-block:: python

    from unittest_parametrize import param
    from unittest_parametrize import parametrize
    from unittest_parametrize import ParametrizedTestCase


    class SquareTests(ParametrizedTestCase):
        @parametrize(
            "x,expected",
            [
                param(1, 1, id="one"),
                param(2, 4, id="two"),
            ],
        )
        def test_square(self, x: int, expected: int) -> None:
            self.assertEqual(x**2, expected)

Yielding perhaps more natural names:

.. code-block:: console

    $ python -m unittest t.py -v
    test_square_one (t.SquareTests.test_square_one) ... ok
    test_square_two (t.SquareTests.test_square_two) ... ok

    ----------------------------------------------------------------------
    Ran 2 tests in 0.000s

    OK

Parameter IDs should be valid Python identifier suffixes.

Since parameter IDs are optional, you can provide them only for some tests:

.. code-block:: python

    from unittest_parametrize import param
    from unittest_parametrize import parametrize
    from unittest_parametrize import ParametrizedTestCase


    class SquareTests(ParametrizedTestCase):
        @parametrize(
            "x,expected",
            [
                param(1, 1),
                param(20, 400, id="large"),
            ],
        )
        def test_square(self, x: int, expected: int) -> None:
            self.assertEqual(x**2, expected)

ID-free ``param``\s fall back to the default index suffixes:

.. code-block:: console

    $ python -m unittest t.py -v
    test_square_0 (example.SquareTests.test_square_0) ... ok
    test_square_large (example.SquareTests.test_square_large) ... ok

    ----------------------------------------------------------------------
    Ran 2 tests in 0.000s

    OK

Alternatively, you can provide the id’s separately with the ``ids`` argument:

.. code-block:: python

    from unittest_parametrize import parametrize
    from unittest_parametrize import ParametrizedTestCase


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
            self.assertEqual(x**2, expected)

Use with other test decorators
------------------------------

``@parametrize`` tries to ensure it is the top-most (outermost) decorator.
This limitation exists to ensure that other decorators apply to each parametrized test.
So decorators like ``@mock.patch`` need be beneath ``@parametrize``:

.. code-block:: python

    from unittest import mock
    from unittest_parametrize import parametrize
    from unittest_parametrize import ParametrizedTestCase


    class CarpentryTests(ParametrizedTestCase):
        @parametrize(
            "nails",
            [(11,), (17,)],
        )
        @mock.patch("example.hammer", autospec=True)
        def test_nail_a_board(self, mock_hammer, nails):
            ...

Also note that due to how ``mock.patch`` always adds positional arguments at the start, the parametrized arguments must come last.
``@parametrize`` always adds parameters as keyword arguments, so you can also use `keyword-only syntax <https://peps.python.org/pep-3102/>`__ for parametrized arguments:

.. code-block:: python

    # ...
    def test_nail_a_board(self, mock_hammer, *, nails):
        ...

Multiple ``@parametrize`` decorators
------------------------------------

``@parametrize`` is not stackable.
To create a cross-product of tests, you can use nested list comprehensions:

.. code-block:: python

    from unittest_parametrize import parametrize
    from unittest_parametrize import ParametrizedTestCase


    class RocketTests(ParametrizedTestCase):
        @parametrize(
            "use_ions,hyperdrive_level",
            [
                (use_ions, hyperdrive_level)
                for use_ions in [True, False]
                for hyperdrive_level in [0, 1, 2]
            ],
        )
        def test_takeoff(self, use_ions, hyperdrive_level) -> None:
            ...

The above creates 2 * 3 = 6 versions of ``test_takeoff``.

For larger combinations, |itertools.product()|__ may be more readable:

.. |itertools.product()| replace:: ``itertools.product()``
__ https://docs.python.org/3/library/itertools.html#itertools.product

.. code-block:: python

    from itertools import product
    from unittest_parametrize import parametrize
    from unittest_parametrize import ParametrizedTestCase


    class RocketTests(ParametrizedTestCase):
        @parametrize(
            "use_ions,hyperdrive_level,nose_colour",
            list(
                product(
                    [True, False],
                    [0, 1, 2],
                    ["red", "yellow"],
                )
            ),
        )
        def test_takeoff(self, use_ions, hyperdrive_level, nose_colour) -> None:
            ...

The above creates 2 * 3 * 2 = 12 versions of ``test_takeoff``.

Parametrizing multiple tests in a test case
-------------------------------------------

``@parametrize`` only works as a function decorator, not a class decorator.
To parametrize all tests within a test case, create a separate decorator and apply it to each method:

.. code-block:: python

    from unittest_parametrize import parametrize
    from unittest_parametrize import ParametrizedTestCase


    parametrize_race = parametrize(
        "race",
        [("Human",), ("Halfling",), ("Dwarf",), ("Elf",)],
    )


    class StatsTests(ParametrizedTestCase):
        @parametrize_race
        def test_strength(self, race: str) -> None:
            ...

        @parametrize_race
        def test_dexterity(self, race: str) -> None:
            ...

        ...

History
=======

When I started writing unit tests, I learned to use `DDT (Data-Driven Tests) <https://ddt.readthedocs.io/en/latest/>`__ for parametrizing tests.
It works, but the docs are a bit thin, and the API a little obscure (what does ``@ddt`` stand for again?).

Later when picking up pytest, I learned to use its `parametrization API <https://docs.pytest.org/en/stable/how-to/parametrize.html>`__.
It’s legible and flexible, but it doesn’t work with unittest test cases, which Django’s test tooling provides.

So, until the creation of this package, I was using `parameterized <https://pypi.org/project/parameterized/>`__ on my (Django) test cases.
This package supports parametrization across multiple test runners, though most of them are “legacy” by now.

I created unittest-parametrize as a smaller alternative to *parameterized*, with these goals:

1. Only support unittest test cases.
   For other types of test, you can use pytest’s parametrization.

2. Avoid any custom test runner support.
   Modifying the class at definition time means that all test runners will see the tests the same.

3. Use modern Python features like ``__init_subclass__``.

4. Have full type hint coverage.
   You shouldn’t find unittest-parametrize a blocker when adopting Mypy with strict mode on.

5. Use the name “parametrize” rather than “parameterize”.
   This unification of spelling with pytest should help reduce confusion around the extra “e”.

Thanks to the creators and maintainers of ddt, parameterized, and pytest for their hard work.

Why not subtests?
-----------------

|TestCase.subTest()|__ is unittest’s built-in “parametrization” solution.
You use it in a loop within a single test method:

.. |TestCase.subTest()| replace:: ``TestCase.subTest()``
__ https://docs.python.org/3/library/unittest.html#unittest.TestCase.subTest

.. code-block:: python

    from unittest import TestCase


    class SquareTests(TestCase):
        def test_square(self):
            tests = [
                (1, 1),
                (2, 4),
            ]
            for x, expected in tests:
                with self.subTest(x=x):
                    self.assertEqual(x**2, expected)

This approach crams multiple actual tests into one test method, with several consequences:

* If a subtest fails, it prevents the next subtests from running.
  Thus, failures are harder to debug, since each test run can only give you partial information.

* Subtests can leak state.
  Without correct isolation, they may not test what they appear to.

* Subtests cannot be reordered by tools that detect state leakage, like `pytest-randomly <https://github.com/pytest-dev/pytest-randomly>`__.

* Subtests skew test timings, since the test method runs multiple tests.

* Everything is indented two extra levels for the loop and context manager.

Parametrization avoids all these issues by creating individual test methods.
