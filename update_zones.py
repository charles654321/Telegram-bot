from pymongo import MongoClient
import re

# —— Configuration ——
MONGO_URI        = "mongodb+srv://Telegram_user:Levalar66@cluster0.xtvyffs.mongodb.net/telegram_bot?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME          = "telegram_bot"
COLLECTION_NAME  = "telegram_messages"

# —— Regroupement des variantes arabes par zone canonique ——
ZONE_VARIANTS = {
    "gaza_city":      ["غزة"],
    "rafah":          ["رفح"],
    "khan_younis":    ["خان يونس", "خانيونس"],
    "beit_hanoun":    ["بيت حانون"],
    "jabalia":        ["جباليا"],
    "deir_al_balah":  ["دير البلح"],
    "nuseirat":       ["النصيرات", "نصيرات"],
    "bureij":         ["البريج"],
    "maghazi":        ["المغازي"],
    "shati":          ["الشاطئ"],
    "al_shuja_iya":   ["الشجاعية"],
    "al_zaytoun":     ["الزيتون"],
    "al_tafah":       ["الطفا", "الطفاح"],
    "al_nasr":        ["النصر"],
    "old_gaza":       ["البلدة القديمة", "المدينة القديمة"],
    "sheikh_radwan":  ["الشيخ رضوان"],
    "al_qarara":      ["القرارة"],
    "jaffa_street":   ["شارع يافا"],
    "salah_al_din_street": ["شارع صلاح الدين"],
    "al_shawa_square":["ساحة الشوا", "الشقّة", "الشوا"],  # ajoute toutes les variantes que tu as détectées
    "shakoush":       ["شاكوش"],
    "mawasi":         ["المواسي"],
    "al_firdous":     ["الفردوس"],
    # … complète avec le reste des variantes que tu avais listées
}

def main():
    client     = MongoClient(MONGO_URI)
    collection = client[DB_NAME][COLLECTION_NAME]

    total = 0
    print("🔄 Mise à jour des zones dans MongoDB…")
    for zone, variants in ZONE_VARIANTS.items():
        # construire une regex qui matche l'une OU l'autre variante
        pattern = "|".join(re.escape(v) for v in variants)
        res = collection.update_many(
            {
                "text": {"$regex": pattern}
            },
            {"$set": {"zone": zone}}
        )
        if res.modified_count:
            print(f" • {res.modified_count:4d} docs → zone='{zone}' (pattern: '{pattern}')")
            total += res.modified_count

    print(f"\n✅ {total} documents mis à jour au total.")

if __name__ == "__main__":
    main()
