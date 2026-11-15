"""
Demonstration de bout en bout du chemin legitime (R2 - livrables L9, L11).

Une seule commande, sans ouvrir de terminal supplementaire : on genere une paire
de cles en memoire, on publie v1 et v2, on lance le serveur sur un port libre, et
on fait tourner le robot deux fois. On montre ainsi, de maniere reproductible :
    1. le robot neuf accepte la v2            -> ACCEPTED
    2. relance : rien de nouveau              -> UP_TO_DATE
    3. l'editeur publie une v3                -> ACCEPTED
A la fin, on affiche l'etat du robot et son journal d'audit.

Utilisation (depuis la racine du depot) :
    python -m scripts.demo
"""
import socket
import tempfile
import threading
from contextlib import contextmanager
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric import rsa
from werkzeug.serving import make_server

from client.robot import check_for_update
from client.state import load_state
from server.app import create_app
from server.package_builder import build_package, save_package


@contextmanager
def serveur_actif(packages_dir):
    """Lance le vrai serveur sur un port libre ; le rend joignable le temps de la demo."""
    serveur = make_server("127.0.0.1", 0, create_app(packages_dir))
    fil = threading.Thread(target=serveur.serve_forever, daemon=True)
    fil.start()
    try:
        yield f"http://127.0.0.1:{serveur.server_port}"
    finally:
        serveur.shutdown()
        fil.join()


def titre(n, texte):
    print(f"\n--- {n}. {texte} " + "-" * max(0, 56 - len(texte)))


def main():
    dossier = Path(tempfile.mkdtemp(prefix="demo_ota_"))
    paquets = dossier / "server" / "packages"
    robot = {"state_path": dossier / "client" / "state.json",
             "log_path": dossier / "client" / "audit.log",
             "install_dir": dossier / "client" / "installed"}

    print("Demonstration OTA - chemin legitime (dossier temporaire :", dossier, ")")

    # L'editeur signe v1 et v2 avec sa cle privee (en memoire pour la demo).
    cle = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    for v in (1, 2):
        save_package(build_package(f"firmware v{v}".encode(), v, cle), paquets)

    with serveur_actif(paquets) as url:
        titre(1, "Robot neuf : il doit accepter la derniere version")
        code = check_for_update(url, cle.public_key(), **robot)
        print(f"   -> {code} | version installee : {load_state(robot['state_path'])}")

        titre(2, "On relance : il est deja a jour")
        code = check_for_update(url, cle.public_key(), **robot)
        print(f"   -> {code} | version installee : {load_state(robot['state_path'])}")

        titre(3, "L'editeur publie une v3 : le robot la prend")
        save_package(build_package(b"firmware v3", 3, cle), paquets)
        code = check_for_update(url, cle.public_key(), **robot)
        print(f"   -> {code} | version installee : {load_state(robot['state_path'])}")

    titre(4, "Preuves laissees par le robot")
    print("   logiciel installe :", (robot["install_dir"] / "firmware.bin").read_text())
    print("   client/audit.log :")
    for ligne in robot["log_path"].read_text().splitlines():
        print("     " + ligne)
    print("\nPour les 5 attaques (non signe, modifie, replay, downgrade, MITM) : python -m pytest -v")


if __name__ == "__main__":
    main()
