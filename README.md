# Notre Histoire — Backend

API backend pour l'application de souvenirs en couple "Notre Histoire".

## 🛠️ Prérequis

- **Python** 3.11+
- **PostgreSQL** 16 (via Docker)
- **Docker** & **Docker Compose**

## ⚡ Installation

```bash
# 1. Cloner le projet
git clone <repo-url>
cd notre-histoire-backend

# 2. Créer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3. Installer les dépendances
cd backend
pip install -r requirements.txt
```

## ⚙️ Configuration

Copier le fichier `.env.example` vers `.env` et configurer les variables :

```bash
cp .env.example .env
```

### Variables principales

| Variable | Description | Exemple |
|----------|-------------|---------|
| `DATABASE_URL` | URL de connexion PostgreSQL | `postgresql+asyncpg://user:pass@db:5432/db` |
| `SECRET_KEY` | Clé secrète pour JWT (64+ chars) | `生成 aléatoire` |
| `POSTGRES_USER` | Utilisateur PostgreSQL | `userNH` |
| `POSTGRES_PASSWORD` | Mot de passe PostgreSQL | `adminNH` |
| `POSTGRES_DB` | Nom de la base de données | `notre_histoire` |
| `CORS_ORIGINS` | Origines autorisées (séparées par virgule) | `http://localhost:3000` |
| `MEDIA_ROOT` | Dossier de stockage des médias | `/app/media` |
| `MAX_PHOTO_SIZE_MB` | Taille max photos (MB) | `20` |
| `MAX_VIDEO_SIZE_MB` | Taille max vidéos (MB) | `500` |
| `MAX_AUDIO_SIZE_MB` | Taille max fichiers audio (MB) | `50` |
| `FIRST_ADMIN_EMAIL` | Email du premier admin | `admin@example.com` |
| `FIRST_ADMIN_PASSWORD` | Mot de passe du premier admin | `admin@O123` |

### Configuration email (SMTP)

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM=noreply@notrehistoire.app
```

> **Note** : Pour Gmail, utiliser un [App Password](https://support.google.com/accounts/answer/185833).

## 🚀 Lancement

### Avec Docker (recommandé)

```bash
docker-compose up --build
```

Le backend sera accessible sur `http://localhost:8000`

### En local

```bash
# Démarrer PostgreSQL (Docker)
docker run -d -e POSTGRES_USER=userNH \
  -e POSTGRES_PASSWORD=adminNH \
  -e POSTGRES_DB=notre_histoire \
  -p 5432:5432 postgres:16-alpine

# Lancer le serveur
cd backend
uvicorn app.main:app --reload --port 8000
```

## 📚 Documentation API

Une fois le serveur démarré :

| URL | Description |
|-----|-------------|
| `/docs` | Swagger UI (recommandé) |
| `/redoc` | ReDoc |

## 📁 Structure du projet

```
notre-histoire-backend/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration Pydantic
│   │   ├── database.py        # Connexion SQLAlchemy async
│   │   ├── dependencies.py    # Injection FastAPI
│   │   ├── main.py            # Point d'entrée FastAPI
│   │   ├── crud/              # Opérations base de données
│   │   │   ├── user.py
│   │   │   ├── couple.py
│   │   │   ├── media_item.py
│   │   │   ├── music_track.py
│   │   │   ├── special_date.py
│   │   │   ├── quote.py
│   │   │   └── refresh_token.py
│   │   ├── models/            # Modèles SQLAlchemy
│   │   │   ├── user.py
│   │   │   ├── couple.py
│   │   │   ├── media_item.py
│   │   │   ├── music_track.py
│   │   │   ├── special_date.py
│   │   │   ├── quote.py
│   │   │   └── refresh_token.py
│   │   ├── routers/           # Endpoints API
│   │   │   ├── auth.py        # /api/v1/auth
│   │   │   ├── couple.py      # /api/v1/couple
│   │   │   ├── media.py       # /api/v1/media
│   │   │   ├── music.py       # /api/v1/music
│   │   │   ├── dates.py       # /api/v1/dates
│   │   │   ├── quotes.py      # /api/v1/quotes
│   │   │   └── admin.py       # /api/v1/admin
│   │   ├── schemas/           # Schémas Pydantic (validation)
│   │   ├── services/          # Logique métier
│   │   │   ├── auth_service.py
│   │   │   ├── couple_service.py
│   │   │   ├── media_service.py
│   │   │   ├── music_service.py
│   │   │   └── admin_service.py
│   │   ├── utils/             # Utilitaires
│   │   │   ├── auth.py        # JWT, bcrypt
│   │   │   ├── email.py       # Envoi emails async
│   │   │   └── file_manager.py # Gestion fichiers médias
│   │   └── tests/             # Tests pytest
│   │       └── conftest.py
│   ├── alembic/               # Migrations Alembic
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   ├── requirements.txt       # Dépendances Python
│   ├── pytest.ini
│   ├── alembic.ini
│   ├── Dockerfile
│   └── conftest.py
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## 🧪 Tests

```bash
cd backend
pytest
```

Pour les tests avec couverture :

```bash
cd backend
pytest --cov=app --cov-report=html
```

## 🔧 Commandes utiles

### Migrations Alembic

```bash
cd backend

# Créer une migration
alembic revision --autogenerate -m "Description"

# Appliquer les migrations
alembic upgrade head

# Revenir en arrière d'une migration
alembic downgrade -1

# Voir l'historique
alembic history
```

### Développement

```bash
# Lancer avec rechargement automatique
cd backend
uvicorn app.main:app --reload --port 8000

# Vérifier la syntaxe Python
ruff check app/

# Formatter le code
ruff format app/
```

### Base de données

```bash
# Se connecter à la DB (Docker)
docker exec -it notre_histoire_db psql -U userNH -d notre_histoire

# Voir les tables
docker exec -it notre_histoire_db psql -U userNH -d notre_histoire -c "\dt"
```

## 📡 API Endpoints

### Authentification
- `POST /api/v1/auth/register` — Inscription
- `POST /api/v1/auth/login` — Connexion
- `POST /api/v1/auth/refresh` — Rafraîchir token
- `POST /api/v1/auth/logout` — Déconnexion
- `GET /api/v1/auth/me` — Profil utilisateur

### Couple
- `POST /api/v1/couple` — Créer un couple
- `GET /api/v1/couple` — Infos du couple
- `PATCH /api/v1/couple` — Modifier le couple
- `DELETE /api/v1/couple` — Dissoudre le couple
- `POST /api/v1/couple/invite` — Inviter un partenaire
- `POST /api/v1/couple/join/{token}` — Rejoindre par token
- `GET /api/v1/couple/timer` — Compteur anniversaires

### Médias
- `GET /api/v1/media` — Liste des médias
- `POST /api/v1/media` — Upload média (photo/video)
- `GET /api/v1/media/{id}` — Détails d'un média
- `PATCH /api/v1/media/{id}` — Modifier un média
- `DELETE /api/v1/media/{id}` — Supprimer un média
- `GET /api/v1/media/{id}/file` — Télécharger le fichier

### Musique
- `GET /api/v1/music` — Liste des pistes
- `POST /api/v1/music` — Upload piste audio
- `PATCH /api/v1/music/{id}` — Modifier une piste
- `DELETE /api/v1/music/{id}` — Supprimer une piste

### Dates spéciales
- `GET /api/v1/dates` — Liste des dates
- `POST /api/v1/dates` — Créer une date
- `GET /api/v1/dates/{id}` — Détails d'une date
- `PATCH /api/v1/dates/{id}` — Modifier une date
- `DELETE /api/v1/dates/{id}` — Supprimer une date

### Citations
- `GET /api/v1/quotes` — Liste des citations
- `POST /api/v1/quotes` — Créer une citation
- `PATCH /api/v1/quotes/{id}` — Modifier une citation
- `DELETE /api/v1/quotes/{id}` — Supprimer une citation

### Admin (requiert rôle `admin`)
- `GET /api/v1/admin/stats` — Statistiques globales
- `GET /api/v1/admin/users` — Liste utilisateurs
- `GET /api/v1/admin/couples` — Liste couples
- `GET /api/v1/admin/media` — Liste médias globaux