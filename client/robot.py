"""
Client robot (R2 - livrable L3) : interroge le serveur, telecharge, verifie, installe.

Un cycle de mise a jour :
    1. GET /latest_version : simple indication, jamais crue (decision 4)
    2. GET /download?version=N
    3. verify_package : forme, signature, hash, version (client/verify.py)
    4. si ACCEPTED : installer, puis enregistrer l'etat, puis journaliser

Utilisation (depuis la racine du depot, serveur lance) :
    python -m client.robot
"""
import argparse
from pathlib import Path

import requests

from client.audit import AUDIT_LOG, log_decision
from client.state import STATE_FILE, load_state, save_state
from client.verify import ACCEPTED, load_public_key, verify_package

# Bloc 1 - Parametres et codes propres au reseau.
DEFAULT_SERVER = "http://127.0.0.1:5001"  # decision 9
INSTALL_DIR = Path("client/installed")
TIMEOUT = 5  # secondes : un serveur muet ne bloque pas le robot
NETWORK_ERROR = "NETWORK_ERROR"
UP_TO_DATE = "UP_TO_DATE"


# Bloc 2 - Un cycle complet de mise a jour.
def check_for_update(server_url, public_key, state_path=STATE_FILE,
                     log_path=AUDIT_LOG, install_dir=INSTALL_DIR):
    """Renvoie le code de la decision (ACCEPTED, un code de rejet, NETWORK_ERROR ou UP_TO_DATE)."""
    last = load_state(state_path)

    # 1. Quelle est la derniere version ? (indication seulement)
    try:
        reponse = requests.get(f"{server_url}/latest_version", timeout=TIMEOUT)
        reponse.raise_for_status()
        announced = reponse.json()["version"]
        if not isinstance(announced, int) or isinstance(announced, bool):
            raise ValueError("version annoncee invalide")
    except (requests.RequestException, ValueError, KeyError, TypeError):
        log_decision(None, "ERROR", NETWORK_ERROR, log_path)
        return NETWORK_ERROR
    if announced <= last:
        return UP_TO_DATE  # rien a telecharger, donc rien a journaliser

    # 2. Telecharger le paquet annonce.
    try:
        reponse = requests.get(f"{server_url}/download", params={"version": announced}, timeout=TIMEOUT)
        reponse.raise_for_status()
    except requests.RequestException:
        log_decision(None, "ERROR", NETWORK_ERROR, log_path)
        return NETWORK_ERROR
    try:
        package = reponse.json()
    except ValueError:
        package = None  # pas du JSON : verify_package repondra MALFORMED_PACKAGE

    # 3. Verifier : la version comparee est celle DU PAQUET signe, pas celle annoncee.
    code, content = verify_package(package, public_key, last)
    version = package.get("version") if isinstance(package, dict) else None
    if not isinstance(version, int) or isinstance(version, bool):
        version = None
    if code != ACCEPTED:
        log_decision(version, "REJECTED", code, log_path)
        return code

    # 4. Installer, puis enregistrer l'etat, puis journaliser (dans cet ordre).
    install_dir = Path(install_dir)
    install_dir.mkdir(parents=True, exist_ok=True)
    (install_dir / "firmware.bin").write_bytes(content)
    save_state(version, state_path)
    log_decision(version, "ACCEPTED", ACCEPTED, log_path)
    return ACCEPTED


# Bloc 3 - Ligne de commande.
def main():
    parser = argparse.ArgumentParser(description="Robot : verifie et installe une mise a jour.")
    parser.add_argument("--server", default=DEFAULT_SERVER)
    parser.add_argument("--key", default="keys/public.pem", help="cle publique du serveur")
    args = parser.parse_args()
    code = check_for_update(args.server, load_public_key(args.key))
    print(f"Decision : {code} | version installee : {load_state()}")


if __name__ == "__main__":
    main()