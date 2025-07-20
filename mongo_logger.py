# mongo_logger.py

import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import timezone

# URI de connexion MongoDB (modifie avec ta vraie URI !)
MONGO_URI = "mongodb+srv://Telegram_user:Levalar66@cluster0.xtvyffs.mongodb.net/telegram_bot?retryWrites=true&w=majority&appName=Cluster0"

# Connexion MongoDB
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_default_database()
collection = db["telegram_messages"]  # Tu peux changer le nom de la collection

async def save_message(data: dict):
    """
    Enregistre un message Telegram dans la base MongoDB.
    `data` est un dictionnaire structuré.
    """
    try:
        # Ajout automatique du fuseau UTC sur les dates
        if "timestamp" in data:
            data["timestamp"] = data["timestamp"].astimezone(timezone.utc)

        await collection.insert_one(data)
        print("✅ Message enregistré dans MongoDB.")
    except Exception as e:
        print(f"❌ Erreur lors de l'insertion MongoDB : {e}")
