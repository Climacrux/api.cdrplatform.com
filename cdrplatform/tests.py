from django.test import TestCase

from .api_key_utils import is_prod_api_key, is_test_api_key


class APIKeyTesterTestCase(TestCase):
    def test_api_key_is_test(self):
        # Valid keys
        self.assertTrue(is_test_api_key(prefix="test_er8s9x0d"))
        self.assertTrue(is_test_api_key(prefix="TeST_sdsasd"))
        self.assertTrue(is_test_api_key(prefix="  test_fdsadfsad   "))
        # Invalid keys
        self.assertFalse(is_test_api_key(prefix="    tost_dsasdfa"))
        self.assertFalse(is_test_api_key(prefix="prod_fdsasdfas"))
        self.assertFalse(is_test_api_key(prefix=2341))
        self.assertFalse(is_test_api_key(prefix=0))
        self.assertFalse(is_test_api_key(prefix={"foo": "bar"}))
        self.assertFalse(is_test_api_key(prefix=()))
        self.assertFalse(is_test_api_key(prefix=[1, 2]))

    def test_api_key_is_prod(self):
        # Valid keys
        self.assertTrue(is_prod_api_key(prefix="prod_fdsasdfas"))
        self.assertTrue(is_prod_api_key(prefix="    prod_fdsasdfas  "))
        self.assertTrue(is_prod_api_key(prefix="PrOD_dasdfa"))
        # Invalid keys
        self.assertFalse(is_prod_api_key(prefix="test_fdsadfa"))
        self.assertFalse(is_prod_api_key(prefix=2341))
        self.assertFalse(is_prod_api_key(prefix=0))
        self.assertFalse(is_prod_api_key(prefix={"foo": "bar"}))
        self.assertFalse(is_prod_api_key(prefix=()))
        self.assertFalse(is_prod_api_key(prefix=[1, 2]))
