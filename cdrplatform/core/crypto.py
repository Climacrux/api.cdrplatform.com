from django.utils.crypto import get_random_string
from rest_framework_api_key.crypto import KeyGenerator


class TestKeyGenerator(KeyGenerator):
    """Exactly the same as the original KeyGenerator
    but ensures that prefixes start with `test_`."""

    test_prefix = "test_"

    def __init__(self, prefix_length: int = 8 + len(test_prefix)):
        super().__init__(prefix_length)

    def get_prefix(self) -> str:
        return self.test_prefix + get_random_string(
            self.prefix_length - len(self.test_prefix)
        )
