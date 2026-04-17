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

Créer un fichier `.env` à la racine du projet :

```env
# Database
POSTGRES_USER=notre_histoire
POSTGRES_PASSWORD=changez_mot_de_passe
POSTGRES_DB=notre_histoire_db

# Application
SECRET_KEY=votre_cle_secrete_très_longue
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Media
MEDIA_ROOT=./media
UPLOAD_MAX_SIZE=52428800  # 50MB

# Email (optionnel)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

## 🚀 Lancement

### Avec Docker (recommandé)

```bash
docker-compose up --build
```

### En local

```bash
# Démarrer PostgreSQL (Docker)
docker run -d -e POSTGRES_USER=notre_histoire \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=notre_histoire_db \
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
│   │   ├── config.py       # Configuration
│   │   ├── database.py     # Connexion DB
│   │   ├── main.py         # Point d'entrée FastAPI
│   │   ├── crud/           # Opérations DB
│   │   ├── models/         # Modèles SQLAlchemy
│   │   ├── routers/        # Endpoints API
│   │   ├── schemas/        # Schémas Pydantic
│   │   ├── services/       # Logique métier
│   │   └── utils/          # Utilitaires
│   ├── alembic/            # Migrations DB
│   ├── requirements.txt    # Dépendances Python
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🧪 Tests

```bash
cd backend
pytest
```

## 🔧 Commandes utiles

```bash
# Créer une migration
alembic revision --autogenerate -m "Description"

# Appliquer les migrations
alembic upgrade head

# Revenir en arrière
alembic downgrade -1
```