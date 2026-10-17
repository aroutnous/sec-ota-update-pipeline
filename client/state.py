"""
Etat persistant du robot (R2 - livrable L4, decision 7).

Le fichier client/state.json contient {"last_applied_version": N}.
Il vaut 0 au premier demarrage et n'est ecrit qu'apres une installation reussie.
"""
import json
import os
from pathlib import Path

STATE_FILE = Path("client/state.json")


# Bloc 1 - Lire la derniere version appliquee.
def load_state(path=STATE_FILE) -> int:
    path = Path(path)
    if not path.exists():
        return 0  # premier demarrage du robot
    version = json.loads(path.read_text())["last_applied_version"]
    if not isinstance(version, int) or isinstance(version, bool) or version < 0:
        raise ValueError("state.json illisible : last_applied_version invalide")
    return version


# Bloc 2 - Ecrire de facon atomique : fichier temporaire, puis remplacement.
def save_state(version: int, path=STATE_FILE):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w") as f:
        json.dump({"last_applied_version": version}, f)
        f.flush()
        os.fsync(f.fileno())  # les octets sont vraiment sur le disque
    os.replace(tmp, path)  # remplacement en une seule operation : ancien OU nouveau