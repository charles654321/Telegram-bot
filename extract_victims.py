from pymongo import MongoClient
import re

# 🔧 CONFIGURATION
MONGO_URI = "mongodb+srv://Telegram_user:Levalar66@cluster0.xtvyffs.mongodb.net/telegram_bot?retryWrites=true&w=majority"
DB_NAME = "telegram_bot"
COL_NAME = "telegram_messages"

# 🔍 Expressions régulières de détection
PATTERNS_KILLED = [
    r"(\d+)\s*(?:people\s+)?(?:killed|martyrs?|dead|murdered|died)",
    r"number\s+of\s+(?:martyrs|victims):?\s*(\d+)",
    r"(\d+)\s*(?:شهيد|شهداء)"  # arabe translittéré
]

PATTERNS_INJURED = [
    r"(\d+)\s*(?:people\s+)?(?:injured|wounded|hurt)",
    r"number\s+of\s+injured:?\s*(\d+)",
    r"(\d+)\s*(?:مصاب|جرحى)"  # arabe translittéré
]

# ➕ Compter les noms de personnes dans le message
def count_names(text):
    lines = text.split("\n")
    name_like_lines = [l for l in lines if re.search(r"\b[A-Z][a-z]+\s+[A-Z][a-z]+", l)]
    return len(name_like_lines)

def extract_number(text, patterns):
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                continue
    return 0

# 🔌 Connexion MongoDB
client = MongoClient(MONGO_URI)
collection = client[DB_NAME][COL_NAME]

print("🔄 Extraction des victimes en cours...")
updated_count = 0

# 📦 Parcours des documents
cursor = collection.find({ "translated_text": { "$exists": True } })

for doc in cursor:
    text = doc.get("translated_text", "")
    doc_id = doc["_id"]

    killed = extract_number(text, PATTERNS_KILLED)
    injured = extract_number(text, PATTERNS_INJURED)

    # si pas de chiffres explicites, on tente de deviner via noms listés
    if killed == 0:
        guessed = count_names(text)
        if guessed > 0:
            killed = guessed

    # uniquement si on trouve quelque chose
    if killed > 0 or injured > 0:
        collection.update_one(
            { "_id": doc_id },
            { "$set": {
                "victim_killed": killed,
                "victim_injured": injured
            }}
        )
        updated_count += 1

print(f"✅ {updated_count} documents mis à jour avec des champs 'victim_killed' et 'victim_injured'")
