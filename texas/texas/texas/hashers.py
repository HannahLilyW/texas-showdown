from django.contrib.auth.hashers import PBKDF2PasswordHasher

class PBKDF2PasswordHasher600k(PBKDF2PasswordHasher):
    """
    A subclass of PBKDF2PasswordHasher that uses 600,000 iterations.
    """

    iterations = 600000
