"""
Attaques 3 (replay) et 4 (downgrade) contre le systeme complet (R3 - livrable L5).

Mise en place : le robot s'est mis a jour normalement en v2 aupres du vrai serveur.
Ensuite, un serveur pirate annonce une "v5" mais sert un ancien paquet authentique.
Pour chaque attaque on verifie 4 choses : le code, l'etat, le logiciel installe, le journal.
"""
import json

import pytest

from client.robot import check_for_update
from client.state import load_state
from server.app import create_app
from server.package_builder import build_package, save_package
from tests.outils import serveur_actif

VERSION_ANNONCEE = 5  # le pirate pretend publier une v5


@pytest.fixture
def labo(tmp_path, private_key, public_key):
    """Vrai serveur (v1, v2), robot deja passe en v2, dossier vide pour le pirate."""
    vrai = tmp_path / "vrai_serveur"
    for version in (1, 2):
        save_package(build_package(f"firmware v{version}".encode(), version, private_key), vrai)
    robot = {
        "state_path": tmp_path / "robot" / "state.json",
        "log_path": tmp_path / "robot" / "audit.log",
        "install_dir": tmp_path / "robot" / "installed",
    }
    with serveur_actif(create_app(vrai)) as url:
        assert check_for_update(url, public_key, **robot) == "ACCEPTED"  # robot en v2
    pirate = tmp_path / "serveur_pirate"
    pirate.mkdir()
    return {"vrai": vrai, "pirate": pirate, "robot": robot, "public_key": public_key}


def attaquer(labo, paquet):
    """Le pirate publie `paquet` sous le nom v5.json, puis le robot interroge le pirate."""
    (labo["pirate"] / f"v{VERSION_ANNONCEE}.json").write_text(json.dumps(paquet))
    with serveur_actif(create_app(labo["pirate"])) as url:
        return check_for_update(url, labo["public_key"], **labo["robot"])


def rien_n_a_change(labo, code_attendu):
    robot = labo["robot"]
    assert load_state(robot["state_path"]) == 2
    assert (robot["install_dir"] / "firmware.bin").read_bytes() == b"firmware v2"
    ligne = json.loads(robot["log_path"].read_text().splitlines()[-1])
    assert (ligne["decision"], ligne["reason"]) == ("REJECTED", code_attendu)


def test_attaque_3_replay_du_paquet_deja_installe(labo):
    paquet_v2 = json.loads((labo["vrai"] / "v2.json").read_text())
    assert attaquer(labo, paquet_v2) == "VERSION_NOT_NEWER"
    rien_n_a_change(labo, "VERSION_NOT_NEWER")


def test_attaque_4a_downgrade_vers_v1(labo):
    paquet_v1 = json.loads((labo["vrai"] / "v1.json").read_text())
    assert attaquer(labo, paquet_v1) == "VERSION_NOT_NEWER"
    rien_n_a_change(labo, "VERSION_NOT_NEWER")


def test_attaque_4b_v1_avec_version_maquillee(labo):
    paquet_v1 = json.loads((labo["vrai"] / "v1.json").read_text())
    paquet_v1["version"] = VERSION_ANNONCEE  # le pirate maquille la version
    assert attaquer(labo, paquet_v1) == "BAD_SIGNATURE"
    rien_n_a_change(labo, "BAD_SIGNATURE")


def test_controle_une_vraie_v3_passe_encore(labo, private_key):
    """Apres les attaques, le robot accepte toujours une mise a jour legitime."""
    save_package(build_package(b"firmware v3", 3, private_key), labo["vrai"])
    with serveur_actif(create_app(labo["vrai"])) as url:
        assert check_for_update(url, labo["public_key"], **labo["robot"]) == "ACCEPTED"
    assert load_state(labo["robot"]["state_path"]) == 3