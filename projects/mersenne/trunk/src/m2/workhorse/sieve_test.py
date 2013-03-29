#--python--
# 
#
import unittest

import Sieve

class SieveTestCase(unittest.TestCase):

    def setUp(self):
        """Call before every test case."""
        self.foo = Sieve()
        self.file = open( "blah", "r" )

    def tearDown(self):
        """Call after every test case."""
        self.file.close()

    def testA(self):
        """Test case A. note that all test method names must begin with 'test.'"""
        assert foo.bar() == 543, "bar() not calculating values correctly"

    def testB(self):
        """test case B"""
        assert foo+foo == 34, "can't add Foo instances"

    def testC(self):
        """test case C"""
        assert foo.baz() == "blah", "baz() not returning blah correctly"

class OtherTestCase(unittest.TestCase):

    def setUp(self):
        blah_blah_blah()

    def tearDown(self):
        blah_blah_blah()

    def testBlah(self):
        assert self.blahblah == "blah", "blah isn't blahing blahing correctly"


if __name__ == "__main__":
    unittest.main() # run all tests

