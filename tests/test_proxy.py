"""
Premiers tests du proxy MITM (R4 - livrable L6) : robot -> proxy -> vrai serveur.
Les scenarios complets de l'attaque 5 viendront a l'etape 4.
"""
import pytest

from client.robot import NETWORK_ERROR, check_for_update
from client.state import load_state
from proxy.mitm_proxy import create_proxy
from server.app import create_app
from server.package_builder import build_package, save_package
from tests.outils import serveur_actif


@pytest.fixture
def vrai_serveur(tmp_path, private_key):
    paquets = tmp_path / "paquets"
    save_package(build_package(b"firmware v1", 1, private_key), paquets)
    with serveur_actif(create_app(paquets)) as url:
        yield url


@pytest.fixture
def robot(tmp_path):
    return {
        "state_path": tmp_path / "robot" / "state.json",
        "log_path": tmp_path / "robot" / "audit.log",
        "install_dir": tmp_path / "robot" / "installed",
    }


def passer_par_le_proxy(vrai_serveur, mode, captures, public_key, robot):
    with serveur_actif(create_proxy(vrai_serveur, mode, captures)) as proxy:
        return check_for_update(proxy, public_key, **robot)


def test_mode_transparent_installe_et_capture(vrai_serveur, tmp_path, public_key, robot):
    captures = tmp_path / "captures"
    assert passer_par_le_proxy(vrai_serveur, "transparent", captures, public_key, robot) == "ACCEPTED"
    assert load_state(robot["state_path"]) == 1
    assert (captures / "capture_1.json").exists()  # le proxy a garde une copie


def test_contenu_remplace_est_refuse(vrai_serveur, tmp_path, public_key, robot):
    code = passer_par_le_proxy(vrai_serveur, "tamper-content", tmp_path / "c", public_key, robot)
    assert code == "HASH_MISMATCH"
    assert load_state(robot["state_path"]) == 0
    assert not (robot["install_dir"] / "firmware.bin").exists()


def test_reponses_bloquees_deni_de_service(vrai_serveur, tmp_path, public_key, robot):
    code = passer_par_le_proxy(vrai_serveur, "drop", tmp_path / "c", public_key, robot)
    assert code == NETWORK_ERROR
    assert load_state(robot["state_path"]) == 0
