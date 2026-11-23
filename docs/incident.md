# Compte rendu d'incident — v1.1.0

**Symptôme.** Après la mise en service de `ghcr.io/mariem115/app:v1.1.0`, `scripts/wait-healthy.sh` affiche `staging non sain` et se termine par 1. Depuis la machine hôte, `curl` vers `http://localhost:8080/health` ne reçoit pas de réponse (`Empty reply from server`). Le journal affiche `Running on http://127.0.0.1:8080`. Docker marque le conteneur healthy, car son contrôle interroge `127.0.0.1` à l'intérieur du conteneur.

**Cause.** Le commit `629ae2d`, tag `v1.1.0`, fait écouter l'application sur `127.0.0.1` par défaut. Les tests restent verts : ils utilisent le client de test Flask et n'ouvrent pas le port.

**Correction.** Aucune nouvelle image. Retour à l'image déjà publiée avec `IMAGE_TAG=v1.0.0 docker compose -f compose.staging.yaml up -d --no-build`. Le script affiche `staging sain` et se termine par 0. Le journal affiche `Running on all addresses (0.0.0.0)`. Les tags `v1.0.0` et `v1.1.0` restent inchangés.
