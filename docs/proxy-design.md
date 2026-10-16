# Conception du proxy MITM (R4 - L6)

## 1. Position du proxy
```text
robot -> proxy (port 8080) -> vrai serveur (port 5001)
```
*(Note : le port 5001 est utilisé pour le vrai serveur afin d'éviter les conflits avec le service AirPlay Receiver de macOS sur le port 5000).*

## 2. Comment un vrai attaquant se placerait au milieu
Dans un scénario réel, un attaquant mettrait en place une attaque de type ARP *spoofing* sur le réseau local ou du DNS *spoofing* pour rediriger le trafic légitime du robot vers sa propre machine. En conditions de laboratoire, il s'agit d'une simplification : on se contente de pointer explicitement la configuration réseau du robot directement vers le proxy. Dans la réalité, l'interception devrait se faire de manière transparente au niveau de la couche réseau, sans que le client (le robot) n'ait à modifier lui-même ses paramètres de destination initiaux.

## 3. Ce que fait le proxy
Le proxy se positionne en intermédiaire pour intercepter les flux HTTP :
- Il relaie fidèlement les requêtes de mise à jour (`/latest_version` et `/download`) vers le vrai serveur de mise à jour.
- Il archive et conserve une copie locale de tous les paquets qui transitent par lui.
- Il a la capacité d'inspecter, d'intercepter et de modifier dynamiquement les réponses (comme altérer le contenu, modifier les hachages, falsifier les signatures ou manipuler les numéros de version) afin d'exécuter nos scénarios d'attaque en laboratoire.

## 4. Scenarios et resultat attendu

| Scénario du proxy | Code attendu côté robot |
| --- | --- |
| Mode transparent (aucune modification, contrôle) | ACCEPTED |
| Retirer la signature | MALFORMED_PACKAGE |
| Remplacer le contenu (hash et signature d'origine) | HASH_MISMATCH |
| Remplacer contenu + hash | BAD_SIGNATURE |
| Augmenter le numéro de version dans le paquet | BAD_SIGNATURE |
| Rejouer un paquet capturé en annonçant une version plus récente | VERSION_NOT_NEWER |
| Bloquer les réponses | NETWORK_ERROR |

## 5. Outils
- **Flask** : Utilisé pour implémenter le serveur proxy et recevoir les requêtes HTTP envoyées par le robot. Le port 5001 est configuré par défaut pour éviter l'interférence avec l'AirPlay Receiver de macOS.
- **requests** : Utilisé par le proxy pour émettre à son tour les requêtes vers le vrai serveur distant et récupérer les charges utiles ou les métadonnées.

## 6. Limites
- Bien que la signature cryptographique empêche efficacement l'installation d'un faux paquet corrompu ou malveillant, elle ne peut pas empêcher un attaquant de bloquer ou de retarder l'acheminement de la mise à jour, ce qui expose le système à des attaques de type déni de service (DoS).
- L'endpoint `/latest_version` ne fait pas l'objet d'une signature cryptographique, ce qui signifie qu'un attaquant pourrait potentiellement manipuler l'information de version renvoyée, bien qu'aucun faux paquet ne puisse être validé par la suite grâce à la vérification rigoureuse de la signature au moment du téléchargement.
