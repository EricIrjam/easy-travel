# 🔍 GUIDE DE VÉRIFICATION EASY TRAVEL

## ✅ Vérification Manuelle du Système

### 1. 📁 Structure du Projet
Vérifiez que vous avez tous ces fichiers :

```
easy_travel-chatbot/
├── ✅ app_enhanced.py              (Interface Streamlit enrichie)
├── ✅ requirements.txt             (Dépendances Python)
├── ✅ .env                         (Configuration des clés API)
├── ✅ install_and_run.sh          (Script d'installation)
├── ✅ chatbot/
│   └── ✅ bot.py                  (Chatbot IA principal)
├── ✅ services/
│   ├── ✅ local_data_service.py   (Données locales)
│   ├── ✅ weather_service.py      (Service météo)
│   └── ✅ interactive_journey.py  (Parcours interactif)
├── ✅ models/
│   └── ✅ user_profile.py         (Modèles de données)
└── ✅ utils/
    └── ✅ helpers.py              (Utilitaires)
```

### 2. 🔧 Installation des Dépendances

#### Option A: Script Automatique (Recommandé)
```bash
cd /Users/eric/easy_travel-chatbot
./install_and_run.sh
```

#### Option B: Installation Manuelle
```bash
cd /Users/eric/easy_travel-chatbot

# Créer environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# Installer dépendances
pip install --upgrade pip
pip install -r requirements.txt

# Créer répertoires
mkdir -p data/local_data data/user_plans logs
```

### 3. ⚙️ Configuration (.env)

Vérifiez votre fichier `.env` :

```env
OPENAI_API_KEY=sk-proj-IXqSTmQf1tbDOv0YAOAgOJq81hNC7...
MONGODB_URI=mongodb://localhost:27017/
GOOGLE_MAPS_API_KEY=AIzaSyDHltaDCkZLh_Emdv7Brwt-q0o1kORkm9A
OPENWEATHER_API_KEY=demo_key
```

✅ **Clé OpenAI configurée** (obligatoire pour l'IA)  
✅ **Autres clés optionnelles** (l'app fonctionne en mode démo sans elles)

### 4. 🧪 Tests Rapides

#### Test Python de Base
```bash
python3 -c "print('Python fonctionne ✅')"
```

#### Test des Imports Principaux
```bash
python3 -c "
import sys
sys.path.append('.')

# Test Streamlit
try:
    import streamlit
    print('✅ Streamlit installé')
except ImportError:
    print('❌ Streamlit manquant - Relancez l\\'installation')

# Test OpenAI
try:
    import openai
    print('✅ OpenAI installé')
except ImportError:
    print('❌ OpenAI manquant - Relancez l\\'installation')

# Test modules Easy Travel
try:
    from chatbot.bot import EasyTravelChatbot
    print('✅ Chatbot Easy Travel OK')
except ImportError as e:
    print(f'❌ Chatbot: {e}')

try:
    from services.local_data_service import LocalDataService
    print('✅ Service données locales OK')
except ImportError as e:
    print(f'❌ Données locales: {e}')

print('Test terminé')
"
```

### 5. 🚀 Lancement de l'Application

#### Commande Principale
```bash
cd /Users/eric/easy_travel-chatbot
streamlit run app_enhanced.py
```

#### Avec Environnement Virtuel
```bash
cd /Users/eric/easy_travel-chatbot
source .venv/bin/activate
streamlit run app_enhanced.py
```

### 6. 🌐 Accès à l'Interface

L'application se lance automatiquement dans votre navigateur sur :
**http://localhost:8501**

Si ça ne s'ouvre pas automatiquement, copiez cette URL dans votre navigateur.

### 7. 💡 Test des Fonctionnalités

Une fois l'interface ouverte, testez :

#### Test Chat de Base
1. Cliquez sur l'onglet **"Chat Libre"**
2. Tapez : *"Je veux visiter Paris avec 1000€"*
3. Vérifiez que la réponse inclut :
   - Informations météo
   - Suggestions d'attractions
   - Recommandations de restaurants
   - Conseils de transport

#### Test Parcours Guidé
1. Cliquez sur l'onglet **"Parcours Guidé"**
2. Suivez les étapes interactives
3. Vérifiez la barre de progression
4. Complétez quelques étapes

#### Test Génération de Plan
1. Dans le chat, tapez : *"Génère-moi un plan pour Rome"*
2. Vérifiez que le plan contient :
   - Itinéraire jour par jour
   - Attractions avec détails
   - Restaurants recommandés
   - Informations météo
   - Conseils pratiques

### 8. 🔧 Dépannage

#### Problème : Streamlit ne démarre pas
```bash
pip install --upgrade streamlit
streamlit run app_enhanced.py
```

#### Problème : Erreurs d'import
```bash
pip install --upgrade -r requirements.txt
```

#### Problème : Clés API
- Vérifiez votre fichier `.env`
- L'app fonctionne en mode démo sans toutes les clés

#### Problème : Port occupé
```bash
streamlit run app_enhanced.py --server.port 8502
```

### 9. ✅ Checklist de Vérification

- [ ] Tous les fichiers présents
- [ ] Dépendances installées
- [ ] Configuration .env OK
- [ ] Streamlit se lance sans erreur
- [ ] Interface web accessible
- [ ] Chat IA répond correctement
- [ ] Parcours guidé fonctionne
- [ ] Génération de plans opérationnelle
- [ ] Données météo intégrées
- [ ] Sidebar contextuelle affichée

### 10. 🎉 Fonctionnalités Confirmées

Si tous les tests passent, votre système Easy Travel dispose de :

✅ **Chat IA Enrichi** : GPT-4 avec contexte local et météo  
✅ **Données Authentiques** : Paris, Rome, Barcelone détaillées  
✅ **Météo Temps Réel** : Prévisions et conseils personnalisés  
✅ **Parcours Interactif** : 12 étapes guidées personnalisées  
✅ **Interface Moderne** : Design responsive et intuitif  
✅ **Génération Plans** : Itinéraires complets automatiques  

### 🚀 Prêt à l'Utilisation !

Votre assistant voyage IA Easy Travel est **100% opérationnel** !

---

## 📞 Support

Si vous rencontrez des problèmes :

1. **Relancez l'installation** : `./install_and_run.sh`
2. **Vérifiez votre .env** : Clés API correctes
3. **Testez étape par étape** : Suivez ce guide ligne par ligne
4. **Vérifiez les logs** : Messages d'erreur dans le terminal

**Le système est robuste et fonctionne même sans toutes les APIs configurées !**
