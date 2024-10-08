=========
Changelog
=========

1.5.0 (2024-10-08)
------------------

* On Python 3.11+, add `exception notes <https://docs.python.org/3.11/whatsnew/3.11.html#whatsnew311-pep678>`__ xwith parameter values to failures.
  For example, the final line here:

  .. code-block:: console

    $ python -m unittest example
    F
    ======================================================================
    FAIL: test_square_0 (example.SquareTests.test_square_0)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/.../unittest_parametrize/__init__.py", line 52, in test
        return _func(self, *args, **_params, **kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/.../example.py", line 11, in test_square
        self.assertEqual(x**2, expected)
    AssertionError: 1 != 2
    Test parameters: x=1, expected=2

* Drop Python 3.8 support.

* Support Python 3.13.

1.4.0 (2023-10-12)
------------------

* Support whitespace in argument name strings.

  Thanks to Arthur Rio in `PR #47 <https://github.com/adamchainz/unittest-parametrize/pull/47>`__.

1.3.0 (2023-07-10)
------------------

* Drop Python 3.7 support.

1.2.0 (2023-06-16)
------------------

* Make ``param.id`` optional.

  Thanks to Adrien Cossa in `PR #20 <https://github.com/adamchainz/unittest-parametrize/pull/20>`__.

1.1.0 (2023-06-13)
------------------

* Support Python 3.12.

1.0.0 (2023-03-28)
------------------

* First release.
