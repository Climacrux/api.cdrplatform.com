from django.http.request import HttpRequest

from cdrplatform.core.crypto import ProdKeyGenerator, TestKeyGenerator


def is_test_api_key(*, prefix: str) -> bool:
    if not isinstance(prefix, str):
        return False
    return prefix.lower().strip().startswith(TestKeyGenerator.prefix)


def is_prod_api_key(*, prefix: str) -> bool:
    if not isinstance(prefix, str):
        return False
    return prefix.lower().strip().startswith(ProdKeyGenerator.prefix)


def extract_key_from_header(*, request: HttpRequest) -> str:
    try:
        return request.META["HTTP_AUTHORIZATION"].split()[1]
    except IndexError:
        return ""
