"""
Serveur de mise a jour (R1 - livrable L2).

Deux routes, sans authentification : le robot ne fait confiance qu'a la signature.
    GET /latest_version          -> {"version": N}, la plus grande version publiee
    GET /download                -> le paquet de la derniere version
    GET /download?version=N      -> le paquet de la version N

Le serveur ne signe rien : il sert, tels quels, les paquets deja signes par
server/package_builder.py. Port par defaut : 5001 (docs/decisions.md, decision 9).

Utilisation (depuis la racine du depot) :
    python -m server.app
"""
import argparse
import re
from pathlib import Path

from flask import Flask, Response, abort, jsonify, request

from server.package_builder import PACKAGES_DIR

# Bloc 1 - Parametres (decision 9 : 5001, car 5000 est pris par AirPlay sur macOS).
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5001
PACKAGE_NAME = re.compile(r"^v(\d+)\.json$")


# Bloc 2 - Les versions publiees = les fichiers v<N>.json du dossier des paquets.
def available_versions(packages_dir):
    packages_dir = Path(packages_dir)
    if not packages_dir.is_dir():
        return []
    versions = []
    for path in packages_dir.iterdir():
        match = PACKAGE_NAME.match(path.name)
        if match:
            versions.append(int(match.group(1)))
    return sorted(versions)


# Bloc 3 - L'application Flask et ses deux routes.
def create_app(packages_dir=PACKAGES_DIR):
    app = Flask(__name__)
    packages_dir = Path(packages_dir)

    @app.get("/latest_version")
    def latest_version():
        versions = available_versions(packages_dir)
        if not versions:
            abort(404, description="aucun paquet publie")
        return jsonify(version=versions[-1])

    @app.get("/download")
    def download():
        versions = available_versions(packages_dir)
        if not versions:
            abort(404, description="aucun paquet publie")
        asked = request.args.get("version")
        if asked is None:
            version = versions[-1]
        elif asked.isdigit():
            version = int(asked)
        else:
            abort(400, description="version invalide")
        if version not in versions:
            abort(404, description=f"version {version} introuvable")
        # Le fichier est envoye octet pour octet : le serveur ne le modifie jamais.
        body = (packages_dir / f"v{version}.json").read_bytes()
        return Response(body, mimetype="application/json")

    return app


# Bloc 4 - Ligne de commande.
def main():
    parser = argparse.ArgumentParser(description="Serveur de mise a jour OTA.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--packages", default=str(PACKAGES_DIR), help="dossier des paquets signes")
    args = parser.parse_args()
    print(f"Versions publiees : {available_versions(args.packages)}")
    create_app(args.packages).run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()