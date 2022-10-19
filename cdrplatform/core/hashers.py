from django.contrib.auth.hashers import Argon2PasswordHasher


class CDRPlatformArgon2PasswordHasher(Argon2PasswordHasher):
    """Custom password hasher based on Argon2.

    We create this in case we want to override any hashing parameters.

    https://docs.djangoproject.com/en/4.1/topics/auth/passwords/#argon2
    """

    time_cost = 4  # Double the standard time cost
    memory_cost = 1024 * 128  # 128 MB
    parallelism = 12  # 1.5x the default parallelism
