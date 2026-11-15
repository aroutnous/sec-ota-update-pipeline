# Journal de bord des echecs

Tout bug, blocage ou attaque qui passe est note le jour meme. C'est la matiere de la
partie la mieux notee du rapport (analyse honnete, echecs compris).

| Date | Qui | Ce qui s'est passe | Cause | Correction / decision |
| --- | --- | --- | --- | --- |
| 15 oct | Amara | La PR #1 contenait keys/public.pem au lieu de decisions.md | Mauvais fichier ajoute avant le push | git rm --cached ; decision 8 (aucune cle versionnee) ; .gitignore renforce. Lecon : relire git diff --stat avant chaque push |
| 15 oct | Amara | La PR #1 fusionnee en squash, commits individuels perdus | Mode de fusion par defaut de GitHub | Regle d'equipe : "Create a merge commit" pour toutes les PR |
| 15 oct | Equipe | Le depot a ete renomme, les git push echouaient | URL distante obsolete | git remote set-url origin <nouvelle URL> |
| 16 oct | Niagale | FileNotFoundError sur server/packages/faux.json | Fichier genere, non versionne, absent chez elle | Le recreer avec la commande du tour. Lecon : chacun regenere ses fichiers generes |
| 16 oct | Niagale | bash: $'\302\203git': command not found (plusieurs fois) | Caractere invisible venu d'un copier-coller depuis Word | Retaper le debut de la commande |
| 16 oct | Niagale | Titre de PR trop long, coupe par GitHub | Titre mis dans le mauvais champ | Titre court, details dans la description |
| 16 oct | Killian | Test de mutation : en commentant la verif du hash, 2a echoue | Echec VOULU | Confirme que le test 2a mesure vraiment la protection du hash ; restaurer verify.py (git checkout) |
| 17 oct | Landry | Le Bloc-notes de Windows 11 a reformate tout decisions.md | Notepad reformate les tableaux Markdown a l'enregistrement | git restore ; ajout de la ligne par commande (sed). Lecon : jamais le Bloc-notes pour un .md ; relire git diff |
| 17 oct | Landry | Collage d'une commande cat > ... <<'EOF' bloque (terminal en attente) | Ici-document non termine | Ctrl+C ; creer le fichier autrement |
| 17 oct | Amara + Landry | Port 5000 occupe par AirPlay Receiver sur macOS | Service systeme macOS sur le port 5000 | Decision 9 : serveur 5001, proxy 8080 |
| 17 oct | Landry | README de la PR #24 : bloc ouvert avec 4 accents graves, tout le reste affiche comme du code | Caractere en trop au collage | Repere a la relecture, corrige avant fusion (commit f9364ea). Lecon : la relecture croisee sert vraiment |
| 17 oct | Landry | python -c "...\`...\`..." : Bash a interprete les accents graves (substitution de commande), terminal en attente | Accent grave = commande en Bash, meme entre guillemets doubles | Ctrl+C ; generer le caractere avec chr(96). Lecon : guillemets simples ou pas d'accents graves |
| 17 oct | Killian | Test de mutation : en commentant la verif de version, 3 et 4a echouent (4b reste vert) | Echec VOULU | Confirme que 3 et 4a dependent de la version ; 4b est bloque par la signature. Restaurer verify.py |
| 17 oct | Killian | Cloture 5.2 lancee avant la fusion de la PR #19 : le graphe ne montrait que 3 PR | Ordre des etapes | Fusionner d'abord, verifier ensuite ; refaire la capture |
