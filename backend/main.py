from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import mysql.connector
import hashlib
import json
import joblib
import xgboost as xgb
import datetime as datetime
from db import get_db_connection
import numpy as np
import logging
import uuid
import os
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.cluster import KMeans
from fastapi import Query
# Initialisation de l'application FastAPI
# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger le modèle et l'encodeur
model = joblib.load ("xgboost_model.pkl")  # Chargement du modèle XGBoost
label_encoder = joblib.load("label_encoder.pkl")

app = FastAPI()
conn = None

@app.on_event("startup")
def startup():
    global conn
    conn = get_db_connection()
    print("✅ Connected to DB!")

@app.on_event("shutdown")
def shutdown():
    if conn:
        conn.close()
        print("🔌 Connection closed.")
# Configuration CORS pour l'accès depuis Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class IntelligentModels:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")  # Modèle de transformation de texte

    def embed_text(self, text):
        return self.model.encode(text).tolist()  # Convertir en liste Python

# ✅ 2. Initialiser models APRES la définition de la classe
models = IntelligentModels()
class Entreprise(BaseModel):
    reponse_id: int
    nom: str
    entreprise_nom: str
    reponse_texte: str
    question_texte: str
    date_reponse: str 
class ProjetCreate(BaseModel):
    titre: str
    description: str
    montant_recherche: float
    client_id: int
    entreprise_id: int
    statut: Optional[str] = "En attente"
    date_creation: Optional[str] = None
class LoginData(BaseModel):
    email: str
    mot_de_passe: str
class ReponseResponse(BaseModel):
    reponse_id: int
    nom: str  # Nom du client
    entreprise_nom: str  # Nom de l'entreprise
    reponse_texte: str
    date_reponse: str  # La date de réponse convertie en chaîne
    question_texte: str  # Texte de la question
class Question(BaseModel):
    question_id: int
    texte: str
    indicateur_ESG: str
    type_question: str
    options: Optional[List[str]] = None
class EntrepriseFiltre(BaseModel):
    nom: str
    entreprise_id: Optional[int] = None
class UserCreate(BaseModel):
    nom: str
    email: str
    telephone: str
    entreprise_id: Optional[int] = None
    nouvelle_entreprise: Optional[str] = None
    secteur_name: Optional[str] = None
    taille: Optional[str] = None
    chiffre_affaires: Optional[float] = None
    localisation: Optional[str] = None
    mot_de_passe: str
class UtilisateurResponse(BaseModel):
    client_id: int
    nom: str
    email: str
    telephone: str
    date_inscription: str
    entreprise: Optional[str]
class Answer(BaseModel):
    client_id: int
    question_id: int
    reponse_texte: str

class EnhancedRecommendation(BaseModel):
    products: List[str]
    services: List[str]
    confidence: float
    rationale: str
class ProjetStatutUpdate(BaseModel):
    statut: str
def get_labels():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT label FROM question WHERE label IS NOT NULL")
    labels = [row[0] for row in cursor.fetchall()]
    conn.close()
    return labels
@app.get("/projets/exists/{client_id}")
async def has_projet(client_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM projet WHERE client_id = %s", (client_id,))
        result = cursor.fetchone()
        return {"exists": result[0] > 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
@app.get("/projets/by-client/{client_id}")
async def get_projets_by_client(client_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT projet_id, titre, description, montant_recherche, statut, date_creation
            FROM projet
            WHERE client_id = %s
        """, (client_id,))
        projets = cursor.fetchall()

        for p in projets:
            if p["date_creation"]:
                p["date_creation"] = p["date_creation"].strftime("%Y-%m-%d")

        return projets

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {e}")
    finally:
        cursor.close()
        conn.close()

@app.put("/projets/{projet_id}/statut")
async def update_projet_statut(projet_id: int, data: ProjetStatutUpdate):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE projet SET statut = %s WHERE projet_id = %s", (data.statut, projet_id))
        conn.commit()

        return {"message": "✅ Statut mis à jour avec succès"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
@app.get("/projets/all")
async def get_all_projets():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                p.projet_id, 
                p.titre, 
                p.description, 
                p.montant_recherche, 
                p.date_creation, 
                p.statut,
                c.nom AS client_nom,
                e.nom AS entreprise_nom
            FROM projet p
            LEFT JOIN client c ON p.client_id = c.client_id
            LEFT JOIN entreprise e ON p.entreprise_id = e.entreprise_id
        """)
        projets = cursor.fetchall()

        # Formatage des dates
        for p in projets:
            if p["date_creation"]:
                p["date_creation"] = p["date_creation"].strftime("%Y-%m-%d")

        return projets

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {e}")
@app.post("/projets/create")
async def create_projet(projet: ProjetCreate):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Déterminer la date
        if projet.date_creation:
            try:
                date_obj = datetime.strptime(projet.date_creation, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="❌ Format de date invalide (attendu : YYYY-MM-DD)")
        else:
            date_obj = datetime.now()

        # Statut par défaut
        statut = "en attente"

        # 🔐 Insertion avec clés étrangères
        cursor.execute("""
            INSERT INTO projet (entreprise_id, client_id, titre, description, montant_recherche, statut, date_creation)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            projet.entreprise_id,
            projet.client_id,
            projet.titre,
            projet.description,
            projet.montant_recherche,
            statut,
            date_obj
        ))

        conn.commit()
        return {"message": "✅ Projet créé avec succès"}

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Erreur base de données : {err}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {e}")
    finally:
        cursor.close()
        conn.close()
@app.get("/reponses/filtered", response_model=List[Entreprise])
async def get_filtered_reponses(
    entreprise_id: Optional[int] = Query(None, alias="entreprise-id"),  # Filtrer par ID d'entreprise
    start_date: Optional[str] = Query(None, alias="start-date"),  # Filtrer par date de début
    end_date: Optional[str] = Query(None, alias="end-date"),  # Filtrer par date de fin
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Construction de la requête avec les filtres dynamiques
        query = """
            SELECT r.reponse_id, c.nom AS nom, e.nom AS entreprise_nom, r.reponse_texte, q.texte AS question_texte, r.date_reponse
            FROM reponse r
            LEFT JOIN client c ON r.client_id = c.client_id
            LEFT JOIN entreprise e ON c.entreprise_id = e.entreprise_id
            LEFT JOIN question q ON r.question_id = q.question_id
            
        """

        cursor.execute(query)
        reponses = cursor.fetchall()

        if not reponses:
            raise HTTPException(status_code=404, detail="❌ Aucune donnée de réponse trouvée")

        # Conversion de la date de réponse en format chaîne
        for reponse in reponses:
            if reponse["date_reponse"]:
                reponse["date_reponse"] = reponse["date_reponse"].strftime("%Y-%m-%d %H:%M:%S")

        # Convert the result to Pydantic models
        return [ReponseResponse(**rep) for rep in reponses]

    except mysql.connector.Error as err:
        logger.error(f"Erreur de base de données: {err}")
        raise HTTPException(status_code=500, detail="Erreur serveur")
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")
    finally:
        cursor.close()
        conn.close()

@app.get("/utilisateurs/", response_model=List[UtilisateurResponse])
async def get_utilisateurs():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Updated query to exclude admins
        cursor.execute("""
            SELECT c.client_id, c.nom, c.email, c.telephone, c.date_inscription, e.nom AS entreprise
            FROM client c
            LEFT JOIN entreprise e ON c.entreprise_id = e.entreprise_id
            WHERE c.role != 'admin'
        """)
        users = cursor.fetchall()

        if not users:
            logger.warning("No users found.")
            raise HTTPException(status_code=404, detail="❌ Aucune donnée d'utilisateur trouvée")
        
        # Convert the datetime to string for 'date_inscription'
        for user in users:
            if user["date_inscription"]:
                user["date_inscription"] = user["date_inscription"].strftime("%Y-%m-%d %H:%M:%S")

        logger.info(f"Users retrieved: {len(users)}")
        return users
    except mysql.connector.Error as err:
        logger.error(f"Database error: {err}")
        raise HTTPException(status_code=500, detail="Erreur serveur")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")
    finally:
        cursor.close()
        conn.close()

@app.get("/reponses/", response_model=List[ReponseResponse])
async def get_reponses():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # SQL pour obtenir les réponses avec le nom du client et le nom de l'entreprise
        cursor.execute("""
            SELECT r.reponse_id, c.nom AS nom, e.nom AS entreprise_nom,  r.reponse_texte,q.texte AS question_texte, r.date_reponse
            FROM reponse r
            LEFT JOIN client c ON r.client_id = c.client_id
            LEFT JOIN entreprise e ON c.entreprise_id = e.entreprise_id
            LEFT JOIN question q ON r.question_id = q.question_id
        """)
        reponses = cursor.fetchall()

        if not reponses:
            logger.warning("Aucune réponse trouvée.")
            raise HTTPException(status_code=404, detail="❌ Aucune donnée de réponse trouvée")
        
        # Conversion de la date de réponse en format chaîne
        for reponse in reponses:
            if reponse["date_reponse"]:
                reponse["date_reponse"] = reponse["date_reponse"].strftime("%Y-%m-%d %H:%M:%S")

        logger.info(f"Réponses récupérées: {len(reponses)}")
        return reponses

    except mysql.connector.Error as err:
        logger.error(f"Erreur de base de données: {err}")
        raise HTTPException(status_code=500, detail="Erreur serveur")
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")
    finally:
        cursor.close()
        conn.close()
# Authentification utilisateur
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()
from datetime import datetime
from fastapi import Query

@app.post("/login/")
async def login_user(data: LoginData):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM client WHERE email = %s", (data.email,))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=401, detail="❌ Email not found")

        hashed_password = hash_password(data.mot_de_passe)
        if user['mot_de_passe'] != hashed_password:
            raise HTTPException(status_code=401, detail="❌ Incorrect password")

        return {
            "message": "✅ Login successful",
            "user_id": user['client_id'],
            "nom": user['nom'],
            "email": user['email'],
            "entreprise_id": user['entreprise_id']  # Important pour le frontend
        }

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
    finally:
        cursor.close()
        conn.close()
from datetime import datetime
from fastapi import Query


@app.get("/entreprises/", response_model=List[EntrepriseFiltre])
async def get_entreprises():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT entreprise_id, nom FROM entreprise")
        entreprises = cursor.fetchall()

        if not entreprises:
            raise HTTPException(status_code=404, detail="❌ Aucune entreprise trouvée")

        return entreprises

    except mysql.connector.Error as err:
        logger.error(f"Erreur de base de données: {err}")
        raise HTTPException(status_code=500, detail="Erreur serveur")
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")
    finally:
        cursor.close()
        conn.close()

@app.post("/register/")
async def register_user(user: UserCreate):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM client WHERE email = %s", (user.email,))
        if cursor.fetchone()[0] > 0:
            raise HTTPException(status_code=400, detail="❌ Email déjà utilisé")

        if user.entreprise_id is None and user.nouvelle_entreprise:
            cursor.execute(""" 
                INSERT INTO entreprise (nom, secteur_name, taille, chiffre_affaires, localisation)
                VALUES (%s, %s, %s, %s, %s)
            """, (user.nouvelle_entreprise, user.secteur_name, user.taille, user.chiffre_affaires, user.localisation))
            conn.commit()
            cursor.execute("SELECT LAST_INSERT_ID()")
            entreprise_id = cursor.fetchone()[0]
        else:
            entreprise_id = user.entreprise_id

        hashed_password = hash_password(user.mot_de_passe)

        cursor.execute(""" 
            INSERT INTO client (nom, email, telephone, entreprise_id, date_inscription, mot_de_passe)
            VALUES (%s, %s, %s, %s, NOW(), %s)
        """, (user.nom, user.email, user.telephone, entreprise_id, hashed_password))

        conn.commit()
        return {"message": "✅ Utilisateur enregistré avec succès !"}

    except mysql.connector.Error as err:
        logger.error(f"Erreur base de données: {err}")
        raise HTTPException(status_code=500, detail="Erreur serveur")
    finally:
        cursor.close()
        conn.close()
@app.put("/questions/{question_id}")
async def modifier_question(question_id: int, question: Question):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Vérifier si la question existe
        cursor.execute("SELECT * FROM question WHERE question_id = %s", (question_id,))
        existing_question = cursor.fetchone()

        if not existing_question:
            raise HTTPException(status_code=404, detail="❌ Question introuvable")

        # Mise à jour de la question
        cursor.execute("""
            UPDATE question 
            SET texte = %s, indicateur_ESG = %s, type_question = %s, options = %s
            WHERE question_id = %s
        """, (question.texte, question.indicateur_ESG, question.type_question, json.dumps(question.options), question_id))

        conn.commit()
        return {"message": "✅ Question mise à jour avec succès"}

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
    finally:
        cursor.close()
        conn.close()
@app.post("/questions/")
async def create_question(question: Question):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO question (texte, type_question) VALUES (%s, %s)", 
                       (question.texte, question.type_question))
        conn.commit()
        return {"message": "✅ Question ajoutée avec succès!"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()
@app.get("/questions/", response_model=List[Question])
async def get_questions():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT question_id, texte, indicateur_ESG, type_question, options FROM question")
        rows = cursor.fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail="❌ Aucune question trouvée")

        for row in rows:
            if row['options']:
                row['options'] = json.loads(row['options'])

        return rows

    except mysql.connector.Error as err:
        logger.error(f"Erreur base de données: {err}")
        raise HTTPException(status_code=500, detail="Erreur serveur")
    finally:
        cursor.close()
        conn.close()
@app.post("/questions/")
async def ajouter_question(question: Question):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Insérer la question
    cursor.execute("""
        INSERT INTO question (texte, indicateur_ESG, type_question, options)
        VALUES (%s, %s, %s, %s)
    """, (question.texte, question.indicateur_ESG, question.type_question, json.dumps(question.options)))
    
    conn.commit()
    return {"message": "✅ Question ajoutée avec succès !"}
@app.get("/is-admin/{client_id}")
async def is_admin(client_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT role FROM client WHERE client_id = %s", (client_id,))
    user = cursor.fetchone()
    
    if user and user["role"] == "admin":
        return {"is_admin": True}
    return {"is_admin": False}

@app.delete("/utilisateurs/{client_id}")
async def supprimer_utilisateur(client_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Vérifier si l'utilisateur existe
    cursor.execute("SELECT * FROM client WHERE client_id = %s", (client_id,))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="❌ Utilisateur introuvable")

    # Supprimer l'utilisateur
    cursor.execute("DELETE FROM client WHERE client_id = %s", (client_id,))
    conn.commit()
    return {"message": "✅ Utilisateur supprimé avec succès"}

    
@app.delete("/reponses/{reponse_id}")
async def delete_reponse(reponse_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Deleting the response by reponse_id
        cursor.execute("DELETE FROM reponse WHERE reponse_id = %s", (reponse_id,))
        conn.commit()

        return {"message": "Réponse supprimée avec succès"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
    finally:
        cursor.close()
        conn.close()

# Enregistrement des réponses des clients
@app.post("/submit-answers/") 
async def submit_answers(answers: List[Answer]):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        models = IntelligentModels()

        for answer in answers:
            embedding = json.dumps(models.embed_text(answer.reponse_texte))  # Convertir l'embedding en JSON

            cursor.execute(""" 
                INSERT INTO reponse (client_id, question_id, reponse_texte, date_reponse, embedding)
                VALUES (%s, %s, %s, NOW(), %s)
            """, (answer.client_id, answer.question_id, answer.reponse_texte, embedding))

        conn.commit()
        return {"message": "✅ Réponses enregistrées avec embeddings"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")
    finally:
        cursor.close()
        conn.close()

from collections import defaultdict, Counter
import random

def load_dataset():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(""" 
        SELECT r.reponse_texte, q.label 
        FROM reponse r 
        JOIN question q ON r.question_id = q.question_id
        WHERE q.label IS NOT NULL
    """)
    data = cursor.fetchall()

    bonnes_pratiques = {
        "Sols": [
            "Paillage : couverture du sol",
            "Méthodes durables de préparation du sol : courbe de niveau, diguettes",
            "Compostage des déchets de cultures",
            "Aménagement de terrasses sur les pentes supérieures à 15%",
            "Analyse de la qualité des sols pour optimiser la culture des plantes aromatiques"
        ],
        "Eau": [
            "Irrigation goutte à goutte",
            "Récupération des eaux pluviales",
            "Réutilisation des eaux de lavage des produits pour des usages non alimentaires",
            "Installation de compteurs d’eau intelligents pour les unités de transformation"
        ],
        "Énergie": [
            "Mécanisation à petite échelle : pompe solaire",
            "Utilisation de panneaux solaires pour les chambres froides",
            "Équipements de transformation écoénergétiques (séchage, broyage, etc.)",
            "Biogaz à partir de déchets organiques de production"
        ],
        "Biodiversité": [
            "Agroforesterie : haies vives",
            "Polyculture : rotation, culture relais",
            "Utilisation de cultures locales et anciennes pour préserver la diversité",
            "Protection des pollinisateurs dans les zones de culture"
        ],
        "Émissions": [
            "Application de nutriments organiques : fumier, lisier, biofertilisants",
            "Réduction des transports inutiles via circuits courts",
            "Optimisation de la chaîne logistique pour limiter le CO₂",
            "Utilisation d'emballages allégés en carbone",
            "📊 Réalisation d’un bilan carbone / diagnostic Bas Carbone : évaluer les émissions réelles (méthane, intrants, carburants) via un outil reconnu comme Climagri ou CAP’2ER. Pourquoi ? Permet d’accéder aux projets rémunérateurs de séquestration carbone, très valorisés par les bailleurs."
        ],
        "Innovation": [
            "Information sur le climat : prévisions saisonnières",
            "Digitalisation de la chaîne de production (traçabilité via QR code)",
            "Capteurs pour le contrôle de l’humidité dans les séchoirs",
            "Utilisation de plateformes de e-commerce responsables"
        ],
        "Éligibilité": [
            "Adhésion à un groupement de développement agricole (GDA)",
            "Participation à des programmes de mise à niveau environnementale",
            "Candidature à des labels durables (Bio, Local, EcoCert)",
            "Audit initial pour accéder à des financements verts ou subventions"
        ],
        "Conformité": [
            "Respect de la réglementation sur les additifs et conservateurs naturels",
            "Mise en place d’un plan HACCP intégré aux normes ESG",
            "Certification ISO 14001 ou équivalente pour l’environnement",
            "Utilisation de logiciels de conformité et de gestion des stocks"
        ],
        "Déchets": [
            "Compostage des déchets organiques de transformation",
            "Réutilisation des noyaux/fragments pour faire des produits dérivés (poudres, huiles)",
            "Partenariat avec des coopératives de recyclage agroalimentaire",
            "Transformation des eaux usées en énergie ou engrais liquide"
        ]
    }

    autres_solutions = {
        "Eau": [
            "Économie d'eau d'irrigation : pilotage sans capteurs",
            "Solution de pilotage des irrigations avec capteurs",
        ],
        "Sols": [
            "Analyse de l'activité biologique du sol / séquestration carbone",
        ],
        "Énergie": [
            "Biogaz, biodiesel",
            "Énergie renouvelable"
        ],
        "Biodiversité": [
            "Lutte bactériologique naturelle",
            "Association des cultures",
            "Association culture-élevage",
            "Cultures oasiennes à étages",
            "Inoculation de Mycorhize",
        ],
        "Émissions": [
            "Logiciel de bilan de carbone",
            "Transport sécurisé",
        ],
        "Innovation": [
            "Station météo & dashboard agritech",
            "Imagerie satellitaire",
            "Crowdsourcing d’experts",
            "Libre échange de semences paysannes",
            "Reporting ESG",
            "Financement participatif",
        ],
        "Éligibilité": [
            "Audit environnemental initial pour accéder aux financements verts",
            "Utilisation de plateformes nationales de gestion ESG (ex. AgriTech Tunisie)",
            "Accès à des microcrédits verts ou financement participatif",
        ],
        "Conformité": [
            "Certification par des labels locaux (ex. Bio Tunisie, Global GAP)",
            "Audit tiers pour vérifier les bonnes pratiques environnementales",
            "Utilisation de logiciels de conformité réglementaire",
        ],
        "Déchets": [
            "Partenariat avec des coopératives de recyclage agricole",
            "Transformation des déchets organiques en biogaz",
            "Utilisation de sacs biodégradables ou recyclables",
        ]
    }

    # Ajout des bonnes pratiques
    for label, textes in bonnes_pratiques.items():
        for texte in textes:
            data.append({"reponse_texte": texte, "label": label})

    # Ajout des autres solutions
    for label, textes in autres_solutions.items():
        for texte in textes:
            data.append({"reponse_texte": texte, "label": label})

    cursor.close()
    conn.close()

    # Embedding
    models = IntelligentModels()
    X, y = [], []
    for row in data:
        try:
            emb = models.embed_text(row["reponse_texte"])
            X.append(emb)
            y.append(row["label"])
        except Exception as e:
            print("Erreur embedding:", e, "| Texte:", row["reponse_texte"])

    return np.array(X), np.array(y)

@app.post("/train-ml/")
async def train_model():
    X, y = load_dataset()
    
    if X is None or len(X) == 0:
        raise HTTPException(status_code=400, detail="Pas assez de données pour l'entraînement")

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

    model = xgb.XGBClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    joblib.dump(model, "ml_model_xgb.pkl")
    joblib.dump(label_encoder, "label_encoder.pkl")

    print("📌 Catégories du modèle :", label_encoder.classes_)

    # ✅ Partie visualisation de l’importance des features
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]  # Tri décroissant

    # Si tu as des noms de features, tu peux les utiliser ici (sinon ce sera Feature 0, 1, 2, ...)
    feature_names = [f"Feature {i}" for i in range(len(importances))]

    # Création du graphique
    plt.figure(figsize=(10, 6))
    plt.title("📊 Importance des caractéristiques")
    plt.bar(range(len(importances)), importances[indices], align="center")
    plt.xticks(range(len(importances)), [feature_names[i] for i in indices], rotation=90)
    plt.tight_layout()

    # Sauvegarde de l’image avec un nom unique
    graphe = f"feature_importance_{uuid.uuid4().hex}.png"
    image_path = os.path.join("static",graphe )
    os.makedirs("static", exist_ok=True)
    plt.savefig(image_path)
    plt.close()

    return {
        "message": f"🎯 Modèle entraîné avec une précision de {accuracy:.2f}",
        "feature_importance_plot": f"/static/{graphe}"
    }

def recommend_products_services(label, n_max=3):
    bonnes_pratiques = {
        "Sols": [
            "Paillage : couverture du sol",
            "Méthodes durables de préparation du sol : courbe de niveau, diguettes",
            "Compostage des déchets de cultures",
            "Aménagement de terrasses sur les pentes supérieures à 15%",
            "Analyse de la qualité des sols pour optimiser la culture des plantes aromatiques"
        ],
        "Eau": [
            "Irrigation goutte à goutte",
            "Récupération des eaux pluviales",
            "Réutilisation des eaux de lavage des produits pour des usages non alimentaires",
            "Installation de compteurs d’eau intelligents pour les unités de transformation"
        ],
        "Énergie": [
            "Mécanisation à petite échelle : pompe solaire",
            "Utilisation de panneaux solaires pour les chambres froides",
            "Équipements de transformation écoénergétiques (séchage, broyage, etc.)",
            "Biogaz à partir de déchets organiques de production"
        ],
        "Biodiversité": [
            "Agroforesterie : haies vives",
            "Polyculture : rotation, culture relais",
            "Utilisation de cultures locales et anciennes pour préserver la diversité",
            "Protection des pollinisateurs dans les zones de culture"
        ],
        "Émissions": [
            "Application de nutriments organiques : fumier, lisier, biofertilisants",
            "Réduction des transports inutiles via circuits courts",
            "Optimisation de la chaîne logistique pour limiter le CO₂",
            "Utilisation d'emballages allégés en carbone",
            "📊 Réalisation d’un bilan carbone / diagnostic Bas Carbone : évaluer les émissions réelles (méthane, intrants, carburants) via un outil reconnu comme Climagri ou CAP’2ER. Pourquoi ? Permet d’accéder aux projets rémunérateurs de séquestration carbone, très valorisés par les bailleurs."
        ],
        "Innovation": [
            "Information sur le climat : prévisions saisonnières",
            "Digitalisation de la chaîne de production (traçabilité via QR code)",
            "Capteurs pour le contrôle de l’humidité dans les séchoirs",
            "Utilisation de plateformes de e-commerce responsables"
        ],
        "Éligibilité": [
            "Adhésion à un groupement de développement agricole (GDA)",
            "Participation à des programmes de mise à niveau environnementale",
            "Candidature à des labels durables (Bio, Local, EcoCert)",
            "Audit initial pour accéder à des financements verts ou subventions"
        ],
        "Conformité": [
            "Respect de la réglementation sur les additifs et conservateurs naturels",
            "Mise en place d’un plan HACCP intégré aux normes ESG",
            "Certification ISO 14001 ou équivalente pour l’environnement",
            "Utilisation de logiciels de conformité et de gestion des stocks"
        ],
        "Déchets": [
            "Compostage des déchets organiques de transformation",
            "Réutilisation des noyaux/fragments pour faire des produits dérivés (poudres, huiles)",
            "Partenariat avec des coopératives de recyclage agroalimentaire",
            "Transformation des eaux usées en énergie ou engrais liquide"
        ]
    }

    autres_solutions = {
        "Eau": [
            "Économie d'eau d'irrigation : pilotage sans capteurs",
            "Solution de pilotage des irrigations avec capteurs",
        ],
        "Sols": [
            "Analyse de l'activité biologique du sol / séquestration carbone",
        ],
        "Énergie": [
            "Biogaz, biodiesel",
            "Énergie renouvelable"
        ],
        "Biodiversité": [
            "Lutte bactériologique naturelle",
            "Association des cultures",
            "Association culture-élevage",
            "Cultures oasiennes à étages",
            "Inoculation de Mycorhize",
        ],
        "Émissions": [
            "Logiciel de bilan de carbone",
            "Transport sécurisé",
        ],
        "Innovation": [
            "Station météo & dashboard agritech",
            "Imagerie satellitaire",
            "Crowdsourcing d’experts",
            "Libre échange de semences paysannes",
            "Reporting ESG",
            "Financement participatif",
        ],
        "Éligibilité": [
            "Audit environnemental initial pour accéder aux financements verts",
            "Utilisation de plateformes nationales de gestion ESG (ex. AgriTech Tunisie)",
            "Accès à des microcrédits verts ou financement participatif",
        ],
        "Conformité": [
            "Certification par des labels locaux (ex. Bio Tunisie, Global GAP)",
            "Audit tiers pour vérifier les bonnes pratiques environnementales",
            "Utilisation de logiciels de conformité réglementaire",
        ],
        "Déchets": [
            "Partenariat avec des coopératives de recyclage agricole",
            "Transformation des déchets organiques en biogaz",
            "Utilisation de sacs biodégradables ou recyclables",
        ]
    }

    produits = bonnes_pratiques.get(label, [])
    services = autres_solutions.get(label, [])

    # Tirage aléatoire (sans répétition si possible)
    produits_sample = random.sample(produits, min(len(produits), n_max))
    services_sample = random.sample(services, min(len(services), n_max))

    return produits_sample, services_sample
def get_question_label(question_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT label FROM question WHERE question_id = %s", (question_id,))
    label = cursor.fetchone()
    conn.close()
    return label[0] if label else None

import joblib
import numpy as np
from fastapi import HTTPException

# Assuming your IntelligentModels class and recommendation function are available
# Also assuming EnhancedRecommendation is defined

from datetime import datetime

from datetime import datetime
def is_negative_response(response):
    response_lower = response.strip().lower()
    return response_lower in ["non", "pas encore", "je ne sais pas", "jsp", "aucune", "nul", "aucun"]

from fastapi import HTTPException
from collections import Counter, defaultdict
import numpy as np
import joblib
from datetime import datetime

from fastapi.responses import JSONResponse

@app.get("/recommendation_multi/{client_id}")
async def recommend_multi_label(client_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT r.reponse_texte FROM reponse r 
        WHERE r.client_id = %s
    """, (client_id,))
    answers = cursor.fetchall()

    if not answers:
        raise HTTPException(status_code=404, detail="Aucune réponse trouvée")

    model = joblib.load("ml_model_xgb.pkl")
    label_encoder = joblib.load("label_encoder.pkl")
    models = IntelligentModels()

    embeddings = np.array([models.embed_text(a["reponse_texte"]) for a in answers])
    predictions = model.predict(embeddings)
    labels = label_encoder.inverse_transform(predictions)
    label_counts = Counter(labels)

    reco = []
    for label, count in label_counts.items():
        bonnes_pratiques, autres_solutions = recommend_products_services(label)
        reco.append({
            "label": label,
            "count": count,
            "bonnes_pratiques": bonnes_pratiques,
            "autres_solutions": autres_solutions
        })

    reco_text = "### 🔎 Recommandations ESG personnalisées :\n\n"
    for r in reco:
        reco_text += f"🌿 **{r['label'].upper()}** (x{r['count']})\n"
        reco_text += f"✅ Bonnes pratiques : {', '.join(r['bonnes_pratiques']) or '—'}\n"
        reco_text += f"💡 Autres solutions : {', '.join(r['autres_solutions']) or '—'}\n\n"

    cursor.execute("""
        UPDATE client SET 
            recommendation_text = %s,
            confidence_score = %s,
            date_recommendation = %s
        WHERE client_id = %s
    """, (reco_text, 0.95, datetime.now(), client_id))
    conn.commit()

    cursor.close()
    conn.close()

    return JSONResponse(content={"themes": reco, "confidence": 0.95})

@app.get("/check_recommendation/{client_id}")
def check_recommendation(client_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT recommendation_text FROM client WHERE client_id = %s", (client_id,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Client non trouvé")

        recommendation_text = result.get("recommendation_text")
        has_reco = bool(recommendation_text and recommendation_text.strip())

        return {"exists": has_reco}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")
    finally:
        cursor.close()
        conn.close()