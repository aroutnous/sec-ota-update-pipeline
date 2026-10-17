"""
Journal d'audit du robot (R2 - livrable L4, decision 6).

Une ligne JSON par decision, ajoutee a la fin du fichier, jamais modifiee :
    {"ts": "2026-10-17T10:00:00Z", "version": 2, "decision": "ACCEPTED", "reason": "ACCEPTED"}
"""
import json
from datetime import datetime, timezone
from pathlib import Path

AUDIT_LOG = Path("client/audit.log")


def log_decision(version, decision, reason, path=AUDIT_LOG) -> dict:
    """decision : ACCEPTED, REJECTED ou ERROR ; version : None si illisible."""
    entry = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "version": version,
        "decision": decision,
        "reason": reason,
    }
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:  # "a" = ajout a la fin, seulement
        f.write(json.dumps(entry) + "\n")
    return entry