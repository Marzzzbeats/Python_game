
## Fonctionnalités & Utilisation

### 1. Peinture et modification visuelle
- **Clic Gauche + Glisser** : Poser l'outil/obstacle sélectionné sur la case.
- **Clic Droit + Glisser** : Gomme (remplace par du sol vide `.`).
- **Clic Milieu / Molette** : Pipette (sélectionne immédiatement l'obstacle cliqué comme outil actif).
- **Surbrillance en temps réel** : Affiche les coordonnées de la case survolée (`Colonne / Ligne`) et un aperçu transparent de l'outil.
- **Zone de spawn joueur** : Le carré 3x3 bleu au centre indique où apparaît le joueur, afin d'éviter d'y poser des obstacles bloquants.

### 2. Palette d'obstacles (Symboles du jeu)
- `[1] W - Mur` (`Wall`) : Bloque le joueur, ennemis et projectiles.
- `[2] P - Pilier` (`Pillar`) : Grand pilier de décor indestructible.
- `[3] C - Caisse` (`Container`) : Caisse destructible / contenant.
- `[4] B - Baril` (`Barrel`) : Baril destructible.
- `[5] S - Pierre` (`Stone`) : Rocher / pierre d'ornement.
- `[0 / E] . - Gomme / Sol vide` : Case marchable libre.

### 3. Gestion des Salles et des Paliers (Tiers)
- **Palier (Tier)** : Boutons `<` et `>` pour naviguer entre les tiers, `+` pour créer un nouveau palier (`0`, `1`, etc.).
- **Navigation Salles** : Boutons `<` et `>` (ou flèches Gauche / Droite du clavier) pour changer de salle.
- **+ Salle** : Ajoute une nouvelle salle vierge au palier actuel.
- **Dupliquer** : Clone fidèlement la salle active avec son layout et ses ennemis.
- **Supprimer** : Retire la salle active.

### 4. Configuration des Ennemis & Capacité
- **Max ennemis simultanés** : Réglez `max_enemies` avec `+` et `-`.
- **Types d'ennemis supportés** : `CinderImp`, `Gorehound`, `Bloodwing`, `Spikeborn`.
- Ajustez le nombre d'ennemis pour chaque type via les boutons `+` et `-`.

### 5. Outils Rapides & Historique
- **Annuler (Ctrl+Z)** : Annule la dernière modification sur le layout (jusqu'à 50 étapes d'historique).
- **Murs Bord** : Entoure automatiquement la pièce d'une bordure de murs (ou la retire en un clic).
- **Vider** : Réinitialise tout le layout avec du sol vide.
- **Dimensions Grille** : Ajustez le nombre de colonnes et de lignes en temps réel (la disposition existante est préservée).

### 6. Sauvegarde et Sécurité
- **Bouton Sauvegarder (ou Ctrl+S)** : Enregistre directement dans `rooms.json` avec l'indentation et la structure exacte attendue par `RoomManager`.
- **Sauvegarde automatique de secours** : Un fichier `rooms.json.bak` est automatiquement créé à chaque sauvegarde.
- **Recharger** : Recharge le fichier JSON depuis le disque à tout moment.

---

## ⌨️ Raccourcis Clavier

| Touche | Action |
|---|---|
| `Ctrl + S` | Sauvegarder dans `rooms.json` |
| `Ctrl + Z` | Annuler la dernière action |
| `1` à `5` | Sélectionner Mur, Pilier, Caisse, Baril, Pierre |
| `0` ou `E` | Sélectionner la Gomme (Sol vide) |
| `W`, `P`, `C`, `B`, `S` | Sélectionner l'outil correspondant |
| `G` | Afficher / Masquer le quadrillage |
| `Flèche Gauche` / `Flèche Droite` | Salle précédente / Salle suivante |
| `Flèche Haut` / `Flèche Bas` | Palier (Tier) précédent / suivant |
