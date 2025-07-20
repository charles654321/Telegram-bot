# test_mongo.py

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# Remplace l'URI ci-dessous par la tienne, avec le bon user + mot de passe encodé
MONGO_URI = "mongodb+srv://Telegram_user:Levalar66@cluster0.xtvyffs.mongodb.net/telegram_bot?retryWrites=true&w=majority&appName=Cluster0"


async def test_connection():
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client.get_default_database()
        print("✅ Connexion réussie !")
        print("📂 Base de données utilisée :", db.name)

        # Test lecture/écriture
        test_collection = db["test_connection"]
        result = await test_collection.insert_one({"test": "ok"})
        print("📝 Document inséré avec l’ID :", result.inserted_id)

        doc = await test_collection.find_one({"_id": result.inserted_id})
        print("🔍 Document retrouvé :", doc)

        # Nettoyage
        await test_collection.delete_many({})
        print("🧹 Documents supprimés (test nettoyé)")
    except Exception as e:
        print("❌ Erreur de connexion :", str(e))

# Lancer le test
asyncio.run(test_connection())
