from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field
from ..db import get_db_connection
import hashlib

router = APIRouter()

# Data model for user signup
class SignupRequest(BaseModel):
    nom: str = Field(..., min_length=3)
    email: EmailStr
    telephone: str = Field(..., min_length=8, max_length=15)
    entreprise_id: int | None = None
    mot_de_passe: str = Field(..., min_length=8)

# Hashing function for secure passwords
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Signup route
@router.post("/signup", response_model=dict)
async def signup(client: SignupRequest):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor()

    try:
        # Check if email already exists
        cursor.execute("SELECT * FROM client WHERE email = %s", (client.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered.")

        # Insert the new client
        hashed_password = hash_password(client.mot_de_passe)
        cursor.execute("""
            INSERT INTO client (nom, email, telephone, entreprise_id, mot_de_passe)
            VALUES (%s, %s, %s, %s, %s)
        """, (client.nom, client.email, client.telephone, client.entreprise_id, hashed_password))

        conn.commit()

        return {"message": "Account created successfully."}

    except Exception as e:
        conn.rollback()  # Rollback changes if an error occurs
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        conn.close()
