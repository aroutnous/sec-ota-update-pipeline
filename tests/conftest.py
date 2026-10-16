"""
Fixtures partagees par les tests (R3 - livrable L5).

Les tests ne dependent d'aucune cle personnelle : une paire RSA-2048 est
generee en memoire pour chaque session de tests, comme le ferait OpenSSL.
"""
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from server.package_builder import build_package


@pytest.fixture(scope="session")
def private_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture(scope="session")
def public_key(private_key):
    return private_key.public_key()


@pytest.fixture
def paquet_v2(private_key):
    """Un paquet v2 authentique, neuf pour chaque test (on peut le modifier sans risque)."""
    return build_package(b"firmware v2", 2, private_key)