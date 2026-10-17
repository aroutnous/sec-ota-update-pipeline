"""
Outils partages par les tests reseau : lancer une vraie application Flask
(serveur, serveur pirate ou proxy) sur un port libre, le temps d'un test.
"""
import socket
import threading
from contextlib import contextmanager

from werkzeug.serving import make_server


@contextmanager
def serveur_actif(app):
    """Lance l'application sur 127.0.0.1, port choisi par le systeme ; renvoie son URL."""
    serveur = make_server("127.0.0.1", 0, app)  # port 0 = un port libre, sans conflit
    fil = threading.Thread(target=serveur.serve_forever, daemon=True)
    fil.start()
    try:
        yield f"http://127.0.0.1:{serveur.server_port}"
    finally:
        serveur.shutdown()
        fil.join()


def url_injoignable():
    """Une URL ou personne n'ecoute (port libere juste apres l'avoir reserve)."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    return f"http://127.0.0.1:{port}"