"""
Verifie qu'un paquet signe se verifie avec la cle publique SEULE (R1 - critere de L1).

Utilisation :
    python scripts/verifier_paquet.py server/packages/v1.json
"""
import base64
import json
import sys
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from server.package_builder import PSS, signed_bytes  # noqa: E402

package = json.loads(Path(sys.argv[1]).read_text())
public_key_path = sys.argv[2] if len(sys.argv) > 2 else "keys/public.pem"
with open(public_key_path, "rb") as f:
    public_key = serialization.load_pem_public_key(f.read())

try:
    public_key.verify(base64.b64decode(package["signature"]),
                      signed_bytes(package["version"], package["content_hash"]),
                      PSS, hashes.SHA256())
    print(f"OK : la signature du paquet v{package['version']} est valide avec {public_key_path}")
except InvalidSignature:
    print("ECHEC : signature invalide")
    sys.exit(1)