"""
Constructeur de paquets de mise a jour signes (R1 - livrable L1).

Format du paquet (docs/package-spec.md, docs/decisions.md) :
    {"version": entier, "content_hash": sha256 hex, "content": base64, "signature": base64}

Octets signes : version (4 octets, big-endian) + hash SHA-256 brut (32 octets) = 36 octets.

Utilisation (depuis la racine du depot) :
    python -m server.package_builder --version 1 --text "firmware v1"
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# Bloc 1 - Parametres de signature : RSA-PSS avec SHA-256 (sel aleatoire de taille maximale).
PSS = padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH)
PACKAGES_DIR = Path("server/packages")


# Bloc 2 - Les 36 octets exacts qui sont signes.
def signed_bytes(version: int, content_hash_hex: str) -> bytes:
    """Version sur 4 octets big-endian, suivie des 32 octets bruts du hash."""
    return version.to_bytes(4, "big") + bytes.fromhex(content_hash_hex)


# Bloc 3 - Charger la cle privee generee avec OpenSSL.
def load_private_key(path):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


# Bloc 4 - Construire le paquet : hash, signature, encodage base64.
def build_package(content: bytes, version: int, private_key) -> dict:
    if not 0 <= version < 2**32:
        raise ValueError("la version doit tenir sur 4 octets")
    content_hash = hashlib.sha256(content).hexdigest()
    signature = private_key.sign(signed_bytes(version, content_hash), PSS, hashes.SHA256())
    return {
        "version": version,
        "content_hash": content_hash,
        "content": base64.b64encode(content).decode("ascii"),
        "signature": base64.b64encode(signature).decode("ascii"),
    }


# Bloc 5 - Enregistrer le paquet dans server/packages/v<version>.json.
def save_package(package: dict, packages_dir=PACKAGES_DIR) -> Path:
    packages_dir = Path(packages_dir)
    packages_dir.mkdir(parents=True, exist_ok=True)
    path = packages_dir / f"v{package['version']}.json"
    path.write_text(json.dumps(package, indent=2))
    return path


# Bloc 6 - Ligne de commande.
def main():
    parser = argparse.ArgumentParser(description="Construit et signe un paquet de mise a jour.")
    parser.add_argument("--version", type=int, required=True, help="numero de version (entier)")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--text", help="contenu de la mise a jour, en texte")
    source.add_argument("--file", help="fichier contenant la mise a jour")
    parser.add_argument("--key", default="keys/private.pem", help="cle privee du serveur")
    parser.add_argument("--out", default=str(PACKAGES_DIR), help="dossier de sortie")
    args = parser.parse_args()

    content = args.text.encode("utf-8") if args.text is not None else Path(args.file).read_bytes()
    package = build_package(content, args.version, load_private_key(args.key))
    print(f"Paquet signe ecrit : {save_package(package, args.out)}")


if __name__ == "__main__":
    main()