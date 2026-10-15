#!/usr/bin/env bash
# Cree les milestones et les issues L1 a L11 avec la CLI GitHub (gh).
# Usage : gh auth login  puis  bash scripts/create_issues.sh
set -euo pipefail
REPO="aroutnous/sec-ota-update-pipeline"

for m in "S2 - interfaces et paquet signe" "S3 - serveur, client, gel du perimetre" \
         "Session 2 - code qui tourne" "Session 3 - 5 attaques documentees" "Session 4 - soutenance"; do
  gh api "repos/$REPO/milestones" -f title="$m" >/dev/null && echo "milestone: $m"
done

issue() { gh issue create --repo "$REPO" --title "$1" --body "$2" --milestone "$3" >/dev/null && echo "issue: $1"; }

issue "L1 - Cles RSA, format de paquet, constructeur (R1)" "Relecteur : R2. Critere : un paquet signe se verifie avec la cle publique seule." "S2 - interfaces et paquet signe"
issue "L2 - Serveur Flask (R1)" "Relecteur : R3. Critere : /latest_version et /download, plusieurs versions, sans authentification." "S3 - serveur, client, gel du perimetre"
issue "L3 - Client robot : signature, hash, version, etat (R2)" "Relecteur : R1. Critere : update valide acceptee, update alteree rejetee." "Session 2 - code qui tourne"
issue "L4 - Audit log et exemple (R2)" "Relecteur : R4. Critere : chaque decision loguee avec sa raison." "Session 2 - code qui tourne"
issue "L5 - Harnais de test, test de controle, attaques 1 a 4 (R3)" "Relecteur : R2. Critere : attaques rejouables en une commande." "S3 - serveur, client, gel du perimetre"
issue "L6 - Proxy MITM et attaque 5 (R4)" "Relecteur : R3. Critere : le proxy modifie un vrai telechargement." "Session 3 - 5 attaques documentees"
issue "L7 - 5 fiches de resultats d'attaque (R3 et R4)" "Relecture croisee. Modele : docs/attack-sheet-template.md" "Session 3 - 5 attaques documentees"
issue "L8 - Security design document (R1)" "Relecteur : R4. Fichier : docs/security-design.md" "Session 4 - soutenance"
issue "L9 - Code commente et README reproductible (R2)" "Relecteur : R3. Critere : tourne sur machine propre sans modification." "Session 4 - soutenance"
issue "L10 - Rapport technique (R4)" "Chaque membre redige sa section. Plan : docs/report-plan.md" "Session 4 - soutenance"
issue "L11 - Demo et soutenance (tous, R2 coordonne)" "Demo repetee, questions croisees preparees." "Session 4 - soutenance"
