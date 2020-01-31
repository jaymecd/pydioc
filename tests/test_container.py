import unittest

from pydioc import Container


def svc_one():
    def _one():
        return 42

    return _one


def svc_two(one: svc_one, param):
    def _two(arg1: str):
        result = one()
        return f"{arg1.upper()}: {result} [{param}]"

    return _two


def build_container(param):
    return Container(("_one", svc_one), ("two", svc_two, ["_one", lambda: param]),)


class TestContainer(unittest.TestCase):
    def test_basics(self):
        container = build_container(param="my-param")

        self.assertEqual("Container(_one, two)", repr(container))
        self.assertEqual(str(container), repr(container))
        self.assertEqual(2, len(container))
        self.assertIn("_one", container)
        self.assertIn("_one", dir(container))
        self.assertIn("two", container)
        self.assertIn("two", dir(container))

        with self.assertRaisesRegex(LookupError, "IoC: service 'one' is not declared"):
            container.one

        with self.assertRaisesRegex(RuntimeError, "IoC: service '_one' is not public"):
            container._one

        self.assertTrue(callable(container.two))
        self.assertEqual(container.two("answer"), "ANSWER: 42 [my-param]")

        self.assertEqual(container.two, container["two"])

    def test_immutable(self):
        container = build_container(param="my-param")

        with self.assertRaisesRegex(RuntimeError, "IoC: service '_one' is immutable"):
            container._one = lambda: 123

        with self.assertRaisesRegex(RuntimeError, "IoC: service '_one' is immutable"):
            container["_one"] = lambda: 123

        with self.assertRaisesRegex(RuntimeError, "IoC: service 'two' is immutable"):
            del container.two

        with self.assertRaisesRegex(RuntimeError, "IoC: service 'two' is immutable"):
            del container["two"]

    def test_invalid(self):
        with self.assertRaisesRegex(
            ValueError, "IoC: service '_one' error: neither a class nor a function"
        ):
            Container(
                ("_one", 42), ("two", svc_two, ["_one"]),
            )

        with self.assertRaisesRegex(
            RuntimeError,
            "IoC: service 'two' error: service '_zero' is not yet declared",
        ):
            Container(
                ("_one", svc_one), ("two", svc_two, ["_zero"]),
            )

        with self.assertRaisesRegex(
            RuntimeError, "IoC: service 'two' error: invalid type of argument #1: int"
        ):
            Container(
                ("_one", svc_one), ("two", svc_two, ["_one", 42]),
            )

        with self.assertRaisesRegex(
            RuntimeError,
            "IoC: service 'two' error: failed to resolve argument #1: 'int' object has no attribute 'upper'",
        ):
            param = 42

            Container(
                ("_one", svc_one), ("two", svc_two, ["_one", lambda: param.upper()]),
            )
