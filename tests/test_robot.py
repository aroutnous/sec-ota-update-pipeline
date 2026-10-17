"""
Tests du robot contre le vrai serveur (R2 - livrables L3 et L4).
Chaque test a son propre robot : etat, journal et logiciel installe dans un dossier temporaire.
"""
import json

import pytest

from client.robot import NETWORK_ERROR, UP_TO_DATE, check_for_update
from client.state import load_state, save_state
from server.app import create_app
from server.package_builder import build_package, save_package
from tests.outils import serveur_actif, url_injoignable


@pytest.fixture
def robot(tmp_path):
    """Les fichiers d'un robot neuf (version 0)."""
    return {
        "state_path": tmp_path / "robot" / "state.json",
        "log_path": tmp_path / "robot" / "audit.log",
        "install_dir": tmp_path / "robot" / "installed",
    }


@pytest.fixture
def serveur(tmp_path, private_key):
    """Le vrai serveur, qui publie v1 et v2 ; renvoie son URL."""
    paquets = tmp_path / "paquets"
    for version in (1, 2):
        save_package(build_package(f"firmware v{version}".encode(), version, private_key), paquets)
    with serveur_actif(create_app(paquets)) as url:
        yield url


def lignes_du_journal(robot):
    return [json.loads(ligne) for ligne in robot["log_path"].read_text().splitlines()]


def test_mise_a_jour_legitime_installee(serveur, public_key, robot):
    assert check_for_update(serveur, public_key, **robot) == "ACCEPTED"
    assert load_state(robot["state_path"]) == 2
    assert (robot["install_dir"] / "firmware.bin").read_bytes() == b"firmware v2"
    ligne = lignes_du_journal(robot)[-1]
    assert (ligne["version"], ligne["decision"], ligne["reason"]) == (2, "ACCEPTED", "ACCEPTED")


def test_deja_a_jour_rien_ne_change(serveur, public_key, robot):
    check_for_update(serveur, public_key, **robot)
    assert check_for_update(serveur, public_key, **robot) == UP_TO_DATE
    assert len(lignes_du_journal(robot)) == 1  # aucune nouvelle decision


def test_etat_conserve_apres_redemarrage(serveur, public_key, robot):
    check_for_update(serveur, public_key, **robot)
    # "Redemarrer" le robot = relire le fichier depuis le disque.
    assert json.loads(robot["state_path"].read_text()) == {"last_applied_version": 2}
    assert load_state(robot["state_path"]) == 2


def test_serveur_injoignable(public_key, robot):
    assert check_for_update(url_injoignable(), public_key, **robot) == NETWORK_ERROR
    assert load_state(robot["state_path"]) == 0
    ligne = lignes_du_journal(robot)[-1]
    assert (ligne["version"], ligne["decision"], ligne["reason"]) == (None, "ERROR", "NETWORK_ERROR")


def test_etat_ecrit_de_facon_atomique(robot):
    save_state(7, robot["state_path"])
    assert load_state(robot["state_path"]) == 7
    assert not robot["state_path"].with_name("state.json.tmp").exists()