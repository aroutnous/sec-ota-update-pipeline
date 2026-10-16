"""
Verification d'un paquet cote robot (R2 - livrable L3).

Ordre des verifications (docs/decisions.md, decision 4) :
    1. forme du paquet (champs et types) sinon MALFORMED_PACKAGE
    2. signature RSA-PSS                  sinon BAD_SIGNATURE       -> authentique
    3. hash recalcule                     sinon HASH_MISMATCH       -> intacte
    4. version > derniere appliquee       sinon VERSION_NOT_NEWER   -> recente
Si tout passe : ACCEPTED.

Ce fichier n'importe rien du serveur : le robot ne connait que la cle publique
et la specification des 36 octets signes.
"""
import base64
import binascii
import hashlib
import re

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# Bloc 1 - Les codes de decision (decision 5).
ACCEPTED = "ACCEPTED"
MALFORMED_PACKAGE = "MALFORMED_PACKAGE"
BAD_SIGNATURE = "BAD_SIGNATURE"
HASH_MISMATCH = "HASH_MISMATCH"
VERSION_NOT_NEWER = "VERSION_NOT_NEWER"

REQUIRED_FIELDS = ("version", "content_hash", "content", "signature")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
PSS = padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH)


# Bloc 2 - Charger la cle publique (la seule cle que possede le robot).
def load_public_key(path):
    with open(path, "rb") as f:
        return serialization.load_pem_public_key(f.read())


# Bloc 3 - Les memes 36 octets que le serveur (redefinis ici, volontairement).
def signed_bytes(version: int, content_hash_hex: str) -> bytes:
    return version.to_bytes(4, "big") + bytes.fromhex(content_hash_hex)


def _b64(value):
    """Decode du base64 strict ; renvoie None si ce n'en est pas."""
    try:
        return base64.b64decode(value, validate=True)
    except (binascii.Error, TypeError, ValueError):
        return None


# Bloc 4 - La verification complete, dans l'ordre fixe.
def verify_package(package, public_key, last_applied_version: int):
    """Renvoie (code, contenu). Le contenu n'est renvoye que si le code vaut ACCEPTED."""
    # 1. Forme : un dict avec les 4 champs, et les bons types.
    if not isinstance(package, dict) or any(f not in package for f in REQUIRED_FIELDS):
        return MALFORMED_PACKAGE, None
    version = package["version"]
    if not isinstance(version, int) or isinstance(version, bool) or not 0 <= version < 2**32:
        return MALFORMED_PACKAGE, None
    content_hash = package["content_hash"]
    if not isinstance(content_hash, str) or not HEX64.match(content_hash):
        return MALFORMED_PACKAGE, None
    content, signature = _b64(package["content"]), _b64(package["signature"])
    if content is None or signature is None:
        return MALFORMED_PACKAGE, None

    # 2. Authentique : signature des 36 octets, verifiee avec la cle publique.
    try:
        public_key.verify(signature, signed_bytes(version, content_hash), PSS, hashes.SHA256())
    except InvalidSignature:
        return BAD_SIGNATURE, None

    # 3. Intacte : on RECALCULE le hash du contenu recu.
    if hashlib.sha256(content).hexdigest() != content_hash:
        return HASH_MISMATCH, None

    # 4. Recente : strictement superieure a la derniere version appliquee.
    if version <= last_applied_version:
        return VERSION_NOT_NEWER, None

    return ACCEPTED, content