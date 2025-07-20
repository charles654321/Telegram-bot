# tag_tents_and_localities.py

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# --- CONFIGURATION MONGODB ---
MONGO_URI = "mongodb+srv://Telegram_user:Levalar66@cluster0.xtvyffs.mongodb.net/telegram_bot?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "telegram_bot"
COLLECTION_NAME = "telegram_messages"

# --- LOCALITÉS À DÉTECTER ---
LOCALITY_KEYWORDS = {
    "rafah": "rafah",
    "jabalia": "jabalia",
    "khan younis": "khan younis",
    "deir al-balah": "deir al-balah",
    "beit hanoun": "beit hanoun",
    "al-shati": "al-shati",
    "shujaiya": "shujaiya",
    "al-nuseirat": "al-nuseirat",
    "al-bureij": "al-bureij",
    "al-magazi": "al-magazi"
}

async def tag_tents():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    col = db[COLLECTION_NAME]

    query = {
        "category": {
            "$regex": r"^\s*(💥 \[Shelling\]|🔫 \[Shooting\]|🔗 \[Victims\])", "$options": "i"
        },
        "translated_text": {
            "$regex": r"tents?", "$options": "i"
        }
    }

    cursor = col.find(query)
    updated = 0
    found = 0

    print("📡 Recherche des messages contenant 'tent(s)' dans Shelling/Shooting/Victims...\n")

    async for doc in cursor:
        found += 1
        text = doc.get("translated_text", "").lower()
        update_fields = {"mentions_tent": True}

        for kw, loc in LOCALITY_KEYWORDS.items():
            if kw in text:
                update_fields["locality"] = loc
                break

        result = await col.update_one(
            {"_id": doc["_id"]},
            {"$set": update_fields}
        )

        if result.modified_count > 0:
            print(f"✅ {doc['_id']} mis à jour ({update_fields})")
            updated += 1
        else:
            print(f"↪️ {doc['_id']} déjà à jour ou inchangé")

    print(f"\n🔍 Total analysé : {found}")
    print(f"🟢 Mis à jour : {updated}")
    client.close()

if __name__ == "__main__":
    asyncio.run(tag_tents())
