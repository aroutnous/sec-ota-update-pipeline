# Security design document (R1 - livrable L8)

> Projet 3 - Secure OTA Update Pipeline. Ce document explique nos choix de
> securite : contre qui on se protege, ce qu'on protege, comment, et ce qu'on
> ne protege pas. Il s'appuie sur les decisions figees dans docs/decisions.md.

## 1. Objectif de securite

Un robot n'installe une mise a jour que si elle est :

- **authentique** : produite par l'editeur legitime (signature RSA-PSS) ;
- **integre** : non modifiee depuis sa signature (hash SHA-256 recalcule) ;
- **recente** : strictement plus recente que la version deja installee (anti-rollback).

Critere de reussite : 5 attaques sur 5 rejetees, 0 mise a jour falsifiee installee,
1 mise a jour legitime acceptee.

## 2. Modele d'attaquant

Nous supposons un attaquant qui controle le reseau entre le robot et le serveur,
et qui peut aussi prendre le controle du serveur de distribution. Concretement,
il peut :

- lire tout le trafic (il n'y a pas de confidentialite : hors perimetre) ;
- modifier, supprimer, rejouer ou retarder n'importe quel message ;
- se faire passer pour le serveur (serveur pirate, proxy man-in-the-middle) ;
- rejouer d'anciens paquets authentiques qu'il a captures.

Ce qu'il **ne peut pas** faire, et sur quoi repose toute notre securite :

- lire ou voler la **cle privee** de l'editeur, qui ne quitte jamais la machine
  de signature et n'est jamais versionnee ;
- casser RSA-2048 ou SHA-256.

## 3. Actifs a proteger

| Actif | Pourquoi il est critique |
| --- | --- |
| La cle privee de l'editeur | Qui la detient peut signer une mise a jour acceptee par tous les robots. C'est le secret central. |
| L'integrite du logiciel installe sur le robot | Un logiciel pirate installe = controle total du robot. |
| L'etat anti-rollback du robot (last_applied_version) | S'il est remis a zero, un downgrade redevient possible. |

## 4. Choix cryptographiques et leur justification

| Choix | Pourquoi |
| --- | --- |
| **RSA-2048** | Taille de cle standard et sure aujourd'hui ; signatures de 256 octets. |
| **RSA-PSS** (MGF1-SHA256, sel de taille max) | Schema de signature RSA moderne, avec preuve de securite ; le sel aleatoire rend chaque signature differente (deux signatures du meme paquet ne sont pas identiques). |
| **SHA-256** | Empreinte de 32 octets, resistante aux collisions ; standard eprouve. |
| **On signe 36 octets** : version (4 octets big-endian) + hash brut (32 octets) | Longueur fixe, calcul identique cote serveur et cote robot, aucune ambiguite. |
| **La version est signee** (ecart avec l'enonce) | Sinon un attaquant renumerote un vieux paquet authentique pour le faire passer pour neuf. Signer la version rend ce maquillage detectable (BAD_SIGNATURE). |
| **Version = entier** | En texte, "10" < "9" : un downgrade pourrait passer. |

## 5. Gestion de la cle privee

- Chaque membre genere sa paire en local avec OpenSSL ; aucune cle n'est partagee
  ni versionnee (`.gitignore` : `*.pem`, `private*`, `*.key`). Deux regles de
  blocage valent mieux qu'une.
- Le robot ne detient que `keys/public.pem` : il peut verifier, pas signer. Voler
  un robot ne donne donc aucun moyen de signer.
- La signature (editeur) est separee de la distribution (serveur) : prendre le
  controle du serveur ne donne pas la cle privee.

## 6. Protection contre le rollback

- Le robot ecrit `last_applied_version` **apres** une installation reussie, de
  facon atomique (`state.json.tmp` puis `os.replace`). Une coupure laisse
  l'ancien ou le nouveau fichier complet, jamais un fichier a moitie ecrit.
- Si le fichier d'etat est illisible, le robot **s'arrete** au lieu de repartir
  de 0 : repartir de 0 rouvrirait la porte au downgrade.

## 7. Journal d'audit

Une ligne JSON par decision, en ajout seul : `ts` (UTC ISO 8601), `version`,
`decision` (ACCEPTED / REJECTED / ERROR), `reason` (le code). Chaque ligne est
une preuve autonome ; l'ajout seul empeche d'effacer la trace d'une attaque.

## 8. Les 5 attaques et la protection qui bloque chacune

| Attaque | Verification qui bloque | Code |
| --- | --- | --- |
| 1 paquet non signe | forme / signature | MALFORMED_PACKAGE / BAD_SIGNATURE |
| 2 paquet modifie | hash / signature | HASH_MISMATCH / BAD_SIGNATURE |
| 3 replay | version | VERSION_NOT_NEWER |
| 4 downgrade | version / signature | VERSION_NOT_NEWER / BAD_SIGNATURE |
| 5 man-in-the-middle | hash (si modifie) ; sinon deni de service | HASH_MISMATCH / NETWORK_ERROR |

## 9. Menaces non couvertes (limites assumees)

| Menace | Pourquoi non couverte | Piste de production |
| --- | --- | --- |
| **Deni de service** | Un attaquant au milieu peut bloquer les reponses ; aucune signature ne force la livraison. | Detecter (alerte apres plusieurs NETWORK_ERROR), plusieurs miroirs. |
| **Attaque de gel** (/latest_version non signe) | La version annoncee n'est pas signee ; un attaquant peut la figer vers le bas. | Metadonnees signees et datees avec expiration (TUF / Uptane). |
| **Fuite de la cle privee** | Toute la securite tombe. Pas de rotation ni de revocation. | Cle chiffree, HSM, signature hors ligne, hierarchie de cles. |
| **Robot reinitialise** | L'etat revient a 0 ; un vieux paquet authentique serait accepte. | Compteur anti-rollback en memoire materielle (eFuse, TPM). |
| **Confidentialite** | Le logiciel circule en clair ; le TLS est hors perimetre. | HTTPS en defense en profondeur, en plus de la signature. |
| **Installation du logiciel non atomique** | Seul l'etat est atomique ; `firmware.bin` pourrait etre partiel. | Partitions A/B : installer sur l'inactive puis basculer. |

## 10. Conclusion

Notre securite ne fait confiance ni au reseau ni au serveur : seulement a la
signature, dont la cle privee reste secrete. Dans ce modele, l'attaquant peut
empecher une mise a jour (deni de service) mais ne peut jamais en faire
installer une fausse. Les limites ci-dessus sont connues et documentees ; elles
tracent le chemin vers une version de production (modele TUF / Uptane).
