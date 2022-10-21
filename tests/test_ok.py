import unittest

from data_flow_diagram import ok


class TestOk(unittest.TestCase):

    def test_ok(self):
        self.assertTrue(ok())


if __name__ == '__main__':
    unittest.main()
