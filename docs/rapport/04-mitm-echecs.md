# Rapport technique - Partie R4 (Amara SOUNTOURA)

> Sections 4.3, 5.3 et 6 du rapport, et réflexion personnelle 8.4.
> Sources : `docs/proxy-design.md`, `proxy/mitm_proxy.py`, `tests/test_proxy.py`,
> `docs/resultats/attaque-5.md`, `docs/journal-echecs.md`.

### 4.3 Le proxy man-in-the-middle (R4)

Pour l'attaque 5, l'attaquant se place entre le robot et le serveur. En réalité, il
y parviendrait par ARP spoofing ou DNS spoofing ; dans notre laboratoire, on
obtient le même résultat pour le robot en le faisant pointer vers le proxy.

`proxy/mitm_proxy.py` (100 lignes) écoute sur `127.0.0.1:8080`, relaie les requêtes
du robot vers le vrai serveur (5001) et agit selon son mode :

- `transparent` : relaie sans rien changer, et garde une copie de chaque paquet
  dans `proxy/captures/` (ce que verrait un espion) ;
- `tamper-content` : remplace le logiciel par « firmware pirate » en gardant le hash
  et la signature d'origine ;
- `drop` : bloque les réponses (code HTTP 503).

Les trois modes sont testés dans `tests/test_proxy.py` (3 tests), avec un vrai
serveur, le vrai proxy et le vrai robot.

### 5.3 Attaque 5 : man-in-the-middle

| Mode | Réaction du robot | Interprétation |
| --- | --- | --- |
| `transparent` | `ACCEPTED` | Contrôle : une vraie mise à jour passe même à travers le proxy. |
| `tamper-content` | `HASH_MISMATCH` | La modification est détectée ; rien n'est installé. |
| `drop` | `NETWORK_ERROR` | Rien n'est reçu, rien n'est installé : c'est un déni de service. |

Les paquets capturés en mode `transparent` ne donnent aucun avantage : les rejouer
revient à l'attaque 3, arrêtée par la version.

**Leçon.** Un attaquant au milieu peut **empêcher** une mise à jour, mais jamais en
**imposer** une fausse. Le déni de service est la seule chose qu'il obtient ; on
peut le détecter (plusieurs `NETWORK_ERROR` de suite), pas l'empêcher par la
signature. La fiche complète est dans `docs/resultats/attaque-5.md`.

## 6. Échecs rencontrés et analyse

Tous les incidents ont été consignés au fil de l'eau dans `docs/journal-echecs.md`.
Nous les regroupons ici par cause, car c'est ce qui nous a fait progresser.

**1. Erreurs de manipulation Git.** La première PR (#1) contenait la clé publique au
lieu du fichier de décisions ; elle a aussi été fusionnée en « squash », ce qui a
effacé les commits individuels. Ces deux erreurs ont produit deux règles d'équipe :
relire `git diff --stat` avant chaque push, et fusionner toujours en
« merge commit ». Le renommage du dépôt a aussi cassé les push (URL distante à
mettre à jour).

**2. Différences entre nos machines.** Le port 5000 était occupé par AirPlay sous
macOS : nous avons fixé le serveur sur 5001 et le proxy sur 8080 (décision 9). Sous
Windows, le Bloc-notes a reformaté les tableaux Markdown de `decisions.md`, et la
commande `source` n'existe pas dans PowerShell (il faut Git Bash). Le zip des
fichiers de travail se décompressait dans un dossier en double.

**3. Copier-coller et terminal.** Des caractères invisibles venus d'un document Word
ont produit des erreurs `command not found` ; Bash a interprété des accents graves
comme des commandes ; une commande `cat <<EOF` mal terminée a bloqué le terminal.
Leçon : relire ce que l'on colle, et préférer copier les fichiers plutôt que les retaper.

**4. Protection de GitHub.** Un push a été refusé (erreur GH007) parce qu'il aurait
publié une adresse e-mail privée. Solution : configurer l'adresse « noreply »
fournie par GitHub pour le dépôt, puis ré-signer le commit.

**5. Échecs voulus.** Les tests de mutation ont volontairement fait échouer des tests
(2a, 3, 4a) pour prouver qu'ils mesurent bien une protection (voir 4.2).

**Ce qu'aucun incident n'a touché :** aucune attaque n'a fait installer de logiciel
falsifié, et aucune clé privée n'a été versionnée. Les incidents ont porté sur
l'outillage et l'organisation, pas sur la sécurité du système.

**Ce que la relecture croisée a rattrapé :** la clé publique dans la PR #1 et le bloc
de code mal fermé du README (PR #24) ont été repérés à la relecture, avant d'arriver
dans `main`.

## 8.4 Réflexion personnelle - Amara

La difficulté la plus concrète pour moi a été le port du proxy. Dans ma conception de l’attaque 5, le serveur et le proxy étaient inversés par rapport à la décision de l’équipe (serveur 5001, proxy 8080). En travaillant sur le proxy, j’ai aussi compris une limite essentielle : la signature garantit l’authenticité et l’intégrité, pas la disponibilité. Le mode drop bloque la mise à jour sans qu’aucune signature puisse l’empêcher.