# ComfyUI API Connector (Français)

Un node ComfyUI puissant pour l'édition d'images via l'API fal.ai. Ce node donne accès à plusieurs modèles d'IA de pointe pour l'édition d'images via une interface unifiée.

**Ceci est un fork de [ComfyUI-NanoSeed](https://github.com/comrender/ComfyUI-NanoSeed) par comrender, avec des fonctionnalités supplémentaires incluant le support de Seedream 5 Lite et des contrôles NSFW visuels.**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Node-orange)

## 🌟 Caractéristiques

- **8 Modèles IA Puissants** - Accès à Nano Banana, Seedream, Qwen et Flux
- **Support Multi-Images** - Éditez avec jusqu'à 5 images de référence
- **Contrôle NSFW** - Checkbox visuelle pour activer/désactiver le filtrage de contenu
- **Résolution Flexible** - Dimensions personnalisées ou ratios d'aspect prédéfinis
- **Traitement Cloud** - Décharge les tâches GPU intensives vers l'infrastructure fal.ai
- **Génération par Lot** - Créez plusieurs variations en une seule fois

## 📋 Modèles Supportés

| Modèle | ID | Description | Coût par Image | Résolution |
|--------|----|-----------|--------------:|-----------|
| **Nano Banana** | `nano_banana` | Édition rapide et efficace | ~$0.02 | 1K-4K via ratio d'aspect |
| **Nano Banana Pro** | `nano_banana_pro` | Version qualité améliorée | ~$0.03 | 1K-4K configurable |
| **Seedream 4.5** | `seedream_4.5` | Modèle haute résolution de ByteDance | ~$0.035 | 1920-4096px |
| **Seedream 5 Lite** ⭐ | `seedream_5_lite` | Dernier modèle avec recherche web | $0.035 | 2K-3K (2048-3072px) |
| **Qwen Edit Plus** | `qwen_edit_plus` | Édition basée sur instructions | ~$0.04 | Dimensions personnalisées |
| **Flux 2 Edit** | `flux_2_edit` | Éditeur haute fidélité de BFL | ~$0.05 | 512-2048px |
| **Flux 2 Pro** | `flux_2_pro` | Flux de qualité professionnelle | ~$0.08 | Dimensions personnalisées |
| **Flux 2 Flex** | `flux_2_flex` | Variante Flux flexible | ~$0.06 | Dimensions personnalisées |

⭐ **Nouveau dans ce fork!**

## 🆕 Nouveautés dans Seedream 5 Lite

Seedream 5 Lite est le dernier modèle d'édition d'images de ByteDance avec plusieurs fonctionnalités avancées:

- **Intégration Recherche Web** - Connaissance en temps réel des événements et tendances actuels
- **Raisonnement Multi-Étapes** - Meilleure compréhension des relations spatiales complexes
- **Rendu de Texte Amélioré** - Typographie précise en plusieurs langues
- **Support d'Images Étendu** - Jusqu'à 14 images de référence (limité à 5 dans l'UI pour simplicité)
- **Génération Séquentielle** - Créez des storyboards et character sheets
- **Ratios d'Aspect Flexibles** - Support de 1:16 à 16:1

## 📥 Installation

### Méthode 1: ComfyUI Manager (Recommandé)

1. Ouvrir ComfyUI Manager
2. Rechercher "API Connector"
3. Cliquer sur Install
4. Redémarrer ComfyUI

### Méthode 2: Installation Manuelle

1. Naviguer vers votre dossier custom nodes ComfyUI:
   ```bash
   cd ComfyUI/custom_nodes/
   ```

2. Cloner ce dépôt:
   ```bash
   git clone https://github.com/votreusername/ComfyUI-APIConnector.git
   ```

3. Installer les dépendances:
   ```bash
   cd ComfyUI-APIConnector
   pip install -r requirements.txt
   ```

4. Redémarrer ComfyUI

## ⚙️ Configuration

### Obtenir une Clé API fal.ai

1. Visiter [fal.ai](https://fal.ai)
2. S'inscrire ou se connecter
3. Aller dans les paramètres API
4. Générer une nouvelle clé API
5. Copier la clé (format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

### Utiliser la Clé API

Entrez votre clé API dans le paramètre `fal_key` du node. Pour plus de sécurité, vous pouvez aussi la définir comme variable d'environnement:

```bash
# Windows PowerShell
$env:FAL_KEY = "votre-cle-api-ici"

# Linux/Mac
export FAL_KEY="votre-cle-api-ici"
```

## 🎨 Utilisation

### Workflow de Base

1. **Ajouter le Node** - Chercher "API Connector" dans ComfyUI
2. **Connecter Images** - Attacher 1-5 images aux entrées
3. **Sélectionner Modèle** - Choisir dans le menu déroulant
4. **Entrer Clé API** - Coller votre clé fal.ai
5. **Écrire le Prompt** - Décrire l'édition désirée
6. **Configurer** - Ajuster résolution, NSFW, seed, etc.
7. **Exécuter** - Lancer le workflow

### 🔒 Contrôle NSFW

Le node inclut une **checkbox NSFW visuelle** qui contrôle le filtrage de contenu:

- **Safe Mode (Défaut)** ✅ - Vérificateur de sécurité activé, filtre le contenu NSFW
- **Allow NSFW** ⚠️ - Vérificateur de sécurité désactivé, autorise le contenu mature

**Modèles Supportés**: Seedream 4.5, Seedream 5 Lite, Qwen Edit Plus, série Flux 2

**Note**: Les modèles Nano Banana n'ont pas de contrôle de vérificateur de sécurité dans l'API.

### Paramètres d'Entrée

#### Requis

- **prompt** (STRING) - Description de l'édition à effectuer
- **model** (DROPDOWN) - Modèle IA à utiliser
- **fal_key** (STRING) - Votre clé API fal.ai

#### Optionnels

- **image1-5** (IMAGE) - Images de référence pour l'édition
- **width/height** (INT) - Dimensions de sortie personnalisées (0 = auto)
- **num_images** (INT) - Nombre de variations à générer (1-6)
- **seed** (INT) - Seed aléatoire pour reproductibilité
- **aspect_ratio** (DROPDOWN) - Ratios prédéfinis (pour modèles Nano)
- **resolution** (DROPDOWN) - Tailles prédéfinies 1K/2K/4K
- **enable_nsfw** (BOOLEAN) - Autoriser/bloquer le contenu NSFW

## 💡 Exemples de Prompts

### Enhancement
```
"Éclairage de studio professionnel"
"Améliorer les couleurs et le contraste"
"Ajouter une profondeur de champ cinématographique"
```

### Transfert de Style
```
"Transformer en style peinture à l'huile"
"Donner l'apparence d'une photo vintage"
"Convertir en style art anime"
```

### Éditions Créatives
```
"Ajouter un coucher de soleil dramatique en arrière-plan"
"Changer la saison en hiver avec de la neige"
"Ajouter un éclairage cyberpunk néon"
```

## 🔧 Dépannage

### "No images returned from API"

- **Vérifier Clé API** - S'assurer que votre clé fal.ai est valide
- **Vérifier Solde** - Vérifier que vous avez suffisamment de crédits
- **Vérifier Prompt** - Certains prompts peuvent déclencher les filtres de sécurité

### Erreurs de Résolution

- **Seedream 4.5** - Doit être minimum 1920px (les deux dimensions)
- **Seedream 5 Lite** - Vérifier que le ratio d'aspect est entre 1:16 et 16:1
- **Flux 2 Edit** - Doit être dans la plage 512-2048px

### Safety Checker Bloque le Contenu

- Activer la checkbox "Allow NSFW" si approprié
- Reformuler le prompt pour être moins suggestif
- Utiliser un modèle différent (Nano Banana n'a pas de filtre)

## 💰 Estimation des Prix

Basé sur les prix fal.ai (sujets à changement):

| Résolution | Nano | Seedream 5 Lite | Flux 2 Pro |
|-----------|------|-----------------|------------|
| 1K (1024px) | $0.02 | $0.035 | $0.08 |
| 2K (2048px) | $0.03 | $0.035 | $0.10 |
| 4K (4096px) | $0.05 | N/A | $0.15 |

Lot de 4 images = 4x le coût

## 📚 Documentation Complète

- **QUICKSTART.md** - Guide de démarrage rapide (5 minutes)
- **README.md** - Documentation complète (en anglais)
- **TESTING.md** - Guide de test avec 10 cas de test
- **CONTRIBUTING.md** - Comment contribuer
- **CHANGELOG.md** - Historique des versions

## 🌟 Crédits

**Projet Original**: [ComfyUI-NanoSeed](https://github.com/comrender/ComfyUI-NanoSeed) par [comrender](https://github.com/comrender)

**Améliorations du Fork**:
- Ajout du support Seedream 5 Lite
- Implémentation des contrôles NSFW visuels
- Documentation améliorée
- Validation et gestion d'erreurs supplémentaires

**Propulsé Par**: API [fal.ai](https://fal.ai)

## 📄 Licence

Licence MIT - Voir le fichier [LICENSE](LICENSE) pour les détails

Ce projet inclut du code de ComfyUI-NanoSeed (Licence MIT)

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/votreusername/ComfyUI-APIConnector/issues)
- **Discussions**: [GitHub Discussions](https://github.com/votreusername/ComfyUI-APIConnector/discussions)
- **Support fal.ai**: [Discord fal.ai](https://discord.gg/fal-ai)

## ⚠️ Avertissement

Ce node nécessite un compte API fal.ai et génère des coûts basés sur l'utilisation. Les utilisateurs sont responsables de:

- Gérer leur utilisation et coûts API
- Se conformer aux conditions d'utilisation de fal.ai
- Utiliser les contrôles NSFW de manière responsable et légale
- Respecter les droits d'auteur et la propriété intellectuelle

Les auteurs ne sont pas responsables des coûts API, du contenu généré, ou de la mauvaise utilisation du logiciel.

---

**⭐ Star ce repo s'il aide votre workflow!**
