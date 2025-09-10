import mysql.connector
import os

# Récupérer les informations de connexion depuis les variables d'environnement
db_host = os.getenv("DB_HOST", "localhost")  # Par défaut 'localhost'
db_user = os.getenv("DB_USER", "root")
db_password = os.getenv("DB_PASSWORD", "Stage123@")
db_name = os.getenv("DB_NAME", "stage")
db_port = int(os.getenv("DB_PORT", 3306))

# Se connecter à la base de données MySQL
try:
    connection = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name,
        port=db_port
    )
    
    cursor = connection.cursor()
    
    # Exemple : lire les entreprises
    cursor.execute("SELECT * FROM entreprise")
    entreprises = cursor.fetchall()
    for entreprise in entreprises:
        print(entreprise)
    
except mysql.connector.Error as err:
    print(f"Erreur de connexion à la base de données : {err}")
finally:
    if cursor:
        cursor.close()
    if connection:
        connection.close()
