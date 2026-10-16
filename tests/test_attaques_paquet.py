"""
Test de controle et attaques 1 et 2 au niveau du paquet (R3 - livrable L5).

Le robot est suppose en version 1. Chaque test suit une ligne de la grille
docs/attack-sheet-template.md ("Resultats attendus").
"""
import base64
import hashlib
import os

from client.verify import (ACCEPTED, BAD_SIGNATURE, HASH_MISMATCH, MALFORMED_PACKAGE,
                           verify_package)

ROBOT_EN_V1 = 1
PIEGE = b"firmware v2 + porte derobee"


def test_controle_mise_a_jour_valide_acceptee(paquet_v2, public_key):
    # Sans ce test, un robot qui rejette TOUT passerait toutes les attaques.
    code, contenu = verify_package(paquet_v2, public_key, ROBOT_EN_V1)
    assert code == ACCEPTED
    assert contenu == b"firmware v2"


def test_attaque_1a_signature_supprimee(paquet_v2, public_key):
    del paquet_v2["signature"]
    assert verify_package(paquet_v2, public_key, ROBOT_EN_V1)[0] == MALFORMED_PACKAGE


def test_attaque_1b_fausse_signature(paquet_v2, public_key):
    paquet_v2["signature"] = base64.b64encode(os.urandom(256)).decode()
    assert verify_package(paquet_v2, public_key, ROBOT_EN_V1)[0] == BAD_SIGNATURE


def test_attaque_2a_contenu_modifie_hash_garde(paquet_v2, public_key):
    paquet_v2["content"] = base64.b64encode(PIEGE).decode()
    assert verify_package(paquet_v2, public_key, ROBOT_EN_V1)[0] == HASH_MISMATCH


def test_attaque_2b_contenu_et_hash_modifies(paquet_v2, public_key):
    paquet_v2["content"] = base64.b64encode(PIEGE).decode()
    paquet_v2["content_hash"] = hashlib.sha256(PIEGE).hexdigest()
    assert verify_package(paquet_v2, public_key, ROBOT_EN_V1)[0] == BAD_SIGNATURE