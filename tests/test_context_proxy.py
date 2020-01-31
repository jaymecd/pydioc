import unittest

from pydioc import ContextProxy


class Sample:
    val = 42

    def __init__(self, param):
        self.param = param

    def format(self):
        return f"Answer to {self.param} is {self.val}"


class TestContextProxy(unittest.TestCase):
    def test_basics(self):
        context = ContextProxy()

        with self.assertRaisesRegex(RuntimeError, "context is not yet set"):
            context.missing

        sample1 = Sample("everything")
        context(sample1)

        with self.assertRaisesRegex(
            LookupError, "context does not have 'missing' attribute"
        ):
            context.missing

        self.assertEqual(sample1.param, context.param)
        self.assertEqual(sample1.format(), context.format())

        sample2 = Sample("universe")
        context(sample2)

        self.assertEqual(sample2.param, context.param)
        self.assertEqual(sample2.format(), context.format())

        self.assertNotEqual(sample1.param, context.param)
