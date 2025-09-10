import time
import mysql.connector
import os

print("⏳ Attente de la base de données...")

while True:
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "db"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT", 3306)),
            auth_plugin='caching_sha2_password'
        )
        print("✅ Connexion à la base de données réussie !")
        conn.close()
        break
    except mysql.connector.Error as err:
        print(f"❌ Erreur de connexion à la base : {err}")
        time.sleep(2)
