#!/usr/bin/env python3
# update_zones_and_verify.py

import re
from pymongo import MongoClient, ASCENDING

# --- CONFIGURATION ---
MONGO_URI = "mongodb+srv://Telegram_user:Levalar66@cluster0.xtvyffs.mongodb.net/telegram_bot?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME   = "telegram_bot"
COL_NAME  = "telegram_messages"

# --- LISTE DES ZONES AVEC VARIANTES ARABE & LATINES ---
ZONES = [
    ("gaza_city",      re.compile(r"(?:غزة|gaza)", re.IGNORECASE)),
    ("rafah",          re.compile(r"(?:رفح|rafah)", re.IGNORECASE)),
    ("khan_younis",    re.compile(r"(?:خان[-\s]?يونس|khan[-\s]?younis)", re.IGNORECASE)),
    ("beit_hanoun",    re.compile(r"(?:بيت\s?حانون|beit[-\s]?hanoun)", re.IGNORECASE)),
    ("jabalia",        re.compile(r"(?:جباليا|jabalia)", re.IGNORECASE)),
    ("deir_al_balah",  re.compile(r"(?:دير\s?البلح|deir[-\s]?al[-\s]?balah)", re.IGNORECASE)),
    ("nuseirat",       re.compile(r"(?:النصيرات|نصيرات|nuseirat)", re.IGNORECASE)),
    ("bureij",         re.compile(r"(?:البريج|bureij)", re.IGNORECASE)),
    ("maghazi",        re.compile(r"(?:المغازي|maghazi)", re.IGNORECASE)),
    ("shati",          re.compile(r"(?:الشاطئ|al[-\s]?shati|shati)", re.IGNORECASE)),
    ("al_shuja_iya",   re.compile(r"(?:الشجاعية|shuja[iy]a|al[-\s]?shuja[iy]a)", re.IGNORECASE)),
    ("al_zaytoun",     re.compile(r"(?:الزيتون|al[-\s]?zaytoun|zaytoun)", re.IGNORECASE)),
    ("al_nasr",        re.compile(r"(?:النصر|al[-\s]?nasr|nasr)", re.IGNORECASE)),
    ("old_gaza",       re.compile(r"(?:البلدة\s?القديمة|المدينة\s?القديمة|old[-\s]?gaza)", re.IGNORECASE)),
    ("sheikh_radwan",  re.compile(r"(?:الشيخ\s?رضوان|sheikh[-\s]?radwan)", re.IGNORECASE)),
    ("al_qarara",      re.compile(r"(?:القرارة|al[-\s]?qarara|qarara)", re.IGNORECASE)),
    ("jaffa_street",   re.compile(r"(?:شارع\s?يافا|jaffa[-\s]?street)", re.IGNORECASE)),
    ("salah_al_din_street", re.compile(r"(?:شارع\s?صلاح\s?الدين|salah[-\s]?al[-\s]?din)(?:[-\s]?street)?", re.IGNORECASE)),
    ("al_shawa_square",    re.compile(r"(?:ساحة\s?الشوا|الشوا|al[-\s]?shawa)(?:[-\s]?square)?", re.IGNORECASE)),
    ("shakoush",       re.compile(r"(?:شاكوش|shakoush)", re.IGNORECASE)),
    ("mawasi",         re.compile(r"(?:المواصي|mawasi)", re.IGNORECASE)),
    ("al_firdous",     re.compile(r"(?:الفردوس|al[-\s]?firdous|firdous)", re.IGNORECASE)),
]

def main():
    client = MongoClient(MONGO_URI)
    coll   = client[DB_NAME][COL_NAME]

    print("🔄 Mise à jour des zones dans MongoDB…")
    total_updated = 0

    for zone_name, pattern in ZONES:
        result = coll.update_many(
            { "zone": { "$exists": False }, "translated_text": { "$regex": pattern } },
            { "$set": { "zone": zone_name } }
        )
        if result.modified_count:
            print(f" • {result.modified_count:4d} docs → zone='{zone_name}' (pattern: {pattern.pattern})")
            total_updated += result.modified_count

    # --- DEBUG : exemples des docs toujours sans zone ---
    missing_cursor = coll.find({ "zone": { "$exists": False } }, { "translated_text": 1 }).limit(10)
    print("\n🧪 Exemples de documents encore sans zone :")
    for doc in missing_cursor:
        txt = doc.get("translated_text", "").replace("\n", " ")[:80]
        print("   →", txt)
    print()

    # --- Vérification finale ---
    missing_count = coll.count_documents({ "zone": { "$exists": False } })
    print(f"🧪 Documents toujours sans zone : {missing_count}")
    print(f"✅ {total_updated} documents mis à jour au total.")

    # --- Création de l’index (MongoDB ignore s’il existe déjà) ---
    print("🔧 Création de l’index sur 'zone'…")
    coll.create_index([("zone", ASCENDING)])
    print("✅ Index créé.")

if __name__ == "__main__":
    main()
