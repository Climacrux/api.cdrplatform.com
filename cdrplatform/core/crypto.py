from django.utils.crypto import get_random_string
from rest_framework_api_key.crypto import KeyGenerator


class PrefixKeyGenerator(KeyGenerator):
    """Exactly the same as the original KeyGenerator
    but ensures that prefixes start with `test_`."""

    prefix = ""

    def __init__(self):
        prefix_length = 8 + len(self.prefix)
        super().__init__(prefix_length)

    def get_prefix(self) -> str:
        return self.prefix + get_random_string(self.prefix_length - len(self.prefix))


class TestKeyGenerator(PrefixKeyGenerator):
    """Exactly the same as the original KeyGenerator
    but ensures that prefixes start with `test_`."""

    prefix = "test_"


class ProdKeyGenerator(PrefixKeyGenerator):
    """Generates a key with `prod_`."""

    prefix = "prod_"
