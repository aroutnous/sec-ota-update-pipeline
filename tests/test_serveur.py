"""
Tests du serveur de mise a jour (R1 - livrable L2).
Le client de test de Flask interroge le serveur sans ouvrir de port reseau.
"""
import json

import pytest

from server.app import create_app
from server.package_builder import build_package, save_package


@pytest.fixture
def client(tmp_path, private_key):
    """Un serveur qui publie v1 et v2, chacun dans un dossier temporaire."""
    for version in (1, 2):
        save_package(build_package(f"firmware v{version}".encode(), version, private_key), tmp_path)
    return create_app(tmp_path).test_client()


def test_latest_version_annonce_la_plus_grande(client):
    reponse = client.get("/latest_version")
    assert reponse.status_code == 200
    assert reponse.get_json() == {"version": 2}


def test_download_sans_parametre_donne_la_derniere(client, tmp_path):
    reponse = client.get("/download")
    assert reponse.status_code == 200
    # Le serveur renvoie le fichier signe octet pour octet.
    assert reponse.data == (tmp_path / "v2.json").read_bytes()


def test_download_sert_plusieurs_versions(client):
    assert json.loads(client.get("/download?version=1").data)["version"] == 1
    assert json.loads(client.get("/download?version=2").data)["version"] == 2


def test_version_inconnue_ou_invalide(client):
    assert client.get("/download?version=9").status_code == 404
    assert client.get("/download?version=abc").status_code == 400


def test_aucun_paquet_publie(tmp_path):
    vide = create_app(tmp_path / "vide").test_client()
    assert vide.get("/latest_version").status_code == 404
    assert vide.get("/download").status_code == 404