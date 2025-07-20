from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, DocumentAttributeVideo
from deep_translator import GoogleTranslator
from datetime import datetime, timezone, timedelta
import os
import json
import hashlib
import re
import asyncio
from sentence_transformers import SentenceTransformer, util
from mongo_logger import save_message

# --- CONFIGURATION ---
api_id = 23811758
api_hash = 'cbfd3db91bd6b98fdcad644153fd7ccd'
session_name = 'session_translate'

# Glossaire des corrections de traduction
OVERRIDES = {
    "Martyrdom": "Victim",
    "Gartan": "Garten",
    "Kawader Kapter": "Quadcopter",
    "Cemetering": "Cemeteries",
    "Mechanisme": "Operations",
    "March": "Missile",
}

# Liste des chaînes sources
source_channels_ids = [
    1394985064,  # الناشط حمزة المصري
    1209608665,  # القسطل الاخباري | القدس
    1434753001,  # اسامة الكحلوت
    1430460151,  # مؤمن مقداد
    2025783593,  # أخبار مدينة دير البلح 🌴
    1475851155,  # رام الله الاخباري
    1007704706   # الجزيرة مباشر
]

# Canaux cibles
target_channel_gaza = -1002525335480
# Ajouter ici l'ID de la chaîne West Bank
target_channel_west_bank = -1002850762542

# Mapping des titres de chaînes
CHANNEL_NAME_MAP = {
    "الناشط حمزة المصري": "Activist Hamza Al-Masry",
    "القسطل الاخباري | القدس": "Al-Qastal News Jerusalem",
    "اسامة الكحلوت": "Osama Al-Kahlout",
    "مؤمن مقداد": "Moamen Meqdad",
    "أخبار مدينة دير البلح 🌴": "Deir Al-Balah News",
    "رام الله الاخباري": "Ramallah News",
    "الجزيرة مباشر": "Aljazeera Mubasher",
    "قناة الجزيرة":    "Aljazeera"
}

def get_translated_channel_title(chat_title):
    return CHANNEL_NAME_MAP.get(chat_title.strip(), chat_title.strip())

# Initialisation des services
client = TelegramClient(session_name, api_id, api_hash)
translator = GoogleTranslator(source='auto', target='en')
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Exemples de catégories pour classification
CATEGORY_EXAMPLES = {
    "💥 [Shelling]": "Israeli artillery fired several shells at a building.",
    "🔫 [Shooting]": "Israeli soldiers opened fire with rifles during a raid.",
    "🔗 [Victims]": "Several civilians were killed in the strike.",
    "⚠️ [Safety]": "Air raid sirens were heard in southern Israel.",
    "🗣️ [Statement]": "The defense minister said operations will continue.",
    "📢 [Announcement]": "Aid trucks will enter Gaza through Rafah crossing.",
    "🧠 [Analysis]": "This reflects a shift in military strategy."
}
CATEGORY_EMBEDDINGS = {
    label: embedding_model.encode(example, convert_to_tensor=True)
    for label, example in CATEGORY_EXAMPLES.items()
}

# Fichiers de persistance
history_file = 'transferred_messages.json'
content_texts_file = 'transferred_texts.json'
MAX_SIMILARITY_HISTORY = 100

# Chargement de l'état précédent
if os.path.exists(history_file):
    with open(history_file, 'r', encoding='utf-8') as f:
        transferred_ids = set(json.load(f))
else:
    transferred_ids = set()
if os.path.exists(content_texts_file):
    with open(content_texts_file, 'r', encoding='utf-8') as f:
        previous_texts = json.load(f)
else:
    previous_texts = []

# Fonctions de sauvegarde
def save_transferred_ids():
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(list(transferred_ids), f)

def save_content_texts():
    with open(content_texts_file, 'w', encoding='utf-8') as f:
        json.dump(previous_texts[-MAX_SIMILARITY_HISTORY:], f)

# Nettoyage du formatage pour comparaison
def strip_formatting(text):
    lines = text.split("\n")
    return "\n".join([l for l in lines if not l.startswith("📰") and not l.startswith("🕒")]).strip()

# Détection de doublon
def is_similar_to_existing(text):
    if not previous_texts:
        return False
    content = strip_formatting(text)
    emb_curr = embedding_model.encode(content, convert_to_tensor=True)
    for old in previous_texts[-MAX_SIMILARITY_HISTORY:]:
        emb_old = embedding_model.encode(strip_formatting(old), convert_to_tensor=True)
        sim = util.cos_sim(emb_curr, emb_old)[0][0].item()
        if sim >= 0.95:
            print(f"⛔ Doublon détecté (sim={sim:.3f})")
            return True
    return False

# Formatage de la date en heure de Gaza
def format_time(ts):
    return ts.astimezone(timezone(timedelta(hours=3))).strftime("%d/%m/%Y %H:%M")

# Détection géographique
def is_about_gaza(text):
    kws = ["gaza","rafah","jabalia","khan younis","deir al-balah","beit hanoun","al-shati","shujaiya","north gaza","south gaza","al-nuseirat","al-bureij","al-magazi"]
    return any(kw in text.lower() for kw in kws)
def is_about_west_bank(text):
    kws = ["west bank","ramallah","nablus","hebron","bethlehem","jenin","jericho","qalqilya","tulkarm","salfit","tubas"]
    return any(kw in text.lower() for kw in kws)

# Filtre religieux
def is_purely_religious_or_reflective(text):
    low = text.lower().strip()
    if not any(k in low for k in ["bomb","strike","victim","killed","shoot","raid","drone","aircraft","injured","hospital","attack"]):
        if any(k in low for k in ["pray","prophet","allah","god","supplication","forgive","paradise","heaven"]):
            if len(re.findall(r'\w+', low)) < 60:
                return True
    return False

# Nettoyage du texte traduit
def sanitize_translated_text(text):
    t = re.sub(r'(?i)^#?urgent[:\s\-]*','', text).strip()
    t = re.sub(r'\n?\d{2}/\d{2}/\d{4} \d{2}:\d{2}$','', t)
    t = re.sub(r'\bmartyr(s)?\b', r'victim\1', t, flags=re.IGNORECASE)
    t = re.sub(r'\b(c(er|he)r?i?m?a?n?s?)\b','victims', t, flags=re.IGNORECASE)
    t = re.sub(r'\b(cemeters?|cemerans?|cemetrans?)\b','victims', t, flags=re.IGNORECASE)
    t = re.sub(r'\boccupation( forces| army| planes| troops|)?\b','IF', t, flags=re.IGNORECASE)
    for wrong, right in OVERRIDES.items():
        t = re.sub(rf"\b{re.escape(wrong)}\b", right, t)
    return t.strip()

# Classification par similarité aux exemples
def classify_message_category(text):
    emb = embedding_model.encode(text, convert_to_tensor=True)
    label = "📜 [Info]"
    best = -1
    for lbl, ex_emb in CATEGORY_EMBEDDINGS.items():
        score = util.cos_sim(emb, ex_emb)[0][0].item()
        if score > best:
            best = score; label = lbl
    low = text.lower()
    if any(k in low for k in ["airstrike","warplane","jet","bombed","strike","missile","explosion","shelling","rocket"]):
        label = "💥 [Shelling]"
    return label

# Formattage final du message
def highlight_locations(text):
    loc_keywords = ["gaza","rafah","jabalia","khan younis","deir al-balah","beit hanoun","al-shati","shujaiya","north gaza","south gaza","al-nuseirat","al-bureij","al-magazi",
                    "west bank","ramallah","nablus","hebron","bethlehem","jenin","jericho","qalqilya","tulkarm","salfit","tubas"]
    pattern = re.compile(r"\b(" + "|".join(re.escape(k) for k in loc_keywords) + r")\b", flags=re.IGNORECASE)
    return pattern.sub(lambda m: f"**{m.group(0)}**", text)

def format_translated_message(channel_title, timestamp, translated_text, original_text=None):
    msg = sanitize_translated_text(translated_text or original_text)
    if not msg or msg.strip() == '.' or len(msg.split()) < 5:
        return None
    if is_purely_religious_or_reflective(msg):
        return None
    if is_similar_to_existing(msg):
        return None
    if channel_title.lower() in ["aljazeera","aljazeera mubasher"]:
        if not (is_about_gaza(msg) or is_about_west_bank(msg)):
            print(f"⛔ Rejeté (Al Jazeera sans localisation): {msg[:80]}")
            return None
    msg = highlight_locations(msg)
    bold_channel = f"**{channel_title}**"
    if re.search(r"\b(evacuat|evacuation|evacuate)\b", msg, flags=re.IGNORECASE):
        header = f"🔴🔴🔴🔴🔴 **{classify_message_category(msg)}**\n📰 [{bold_channel}]"
        msg = f"**{msg}**"
    else:
        header = f"{classify_message_category(msg)}\n📰 [{bold_channel}]"
    time_info = f"🕒 Date : {timestamp} (Gaza Time)"
    return f"{header}\n{time_info}\n\n{msg}"

# Gestion des nouveaux messages
@client.on(events.NewMessage)
async def handler(event):
    m = event.message
    if m.id in transferred_ids:
        return
    if not getattr(m, 'post', False) and getattr(getattr(m, 'from_id', None), 'channel_id', None) != m.peer_id.channel_id:
        return
    original = m.text or getattr(m, 'message', '')
    if not original:
        return
    try:
        trans = translator.translate(original)
        if not trans or not trans.strip():
            print("[⚠️] Traduction vide → original utilisé")
            trans = original
    except Exception as e:
        print(f"Erreur traduction: {e}")
        trans = original
    ts = format_time(m.date)
    raw = event.chat.title if event.chat else 'Unknown'
    chan = get_translated_channel_title(raw)
    formatted = format_translated_message(chan, ts, trans, original)
    if not formatted:
        return

    # ── Intégration MongoDB (uniquement shelling/shooting/victims/safety) ──
    category = classify_message_category(trans)
    if category in ["💥 [Shelling]", "🔫 [Shooting]", "🔗 [Victims]", "⚠️ [Safety]"]:
        await save_message({
            "message_id":      m.id,
            "channel":         chan,
            "timestamp":       m.date,
            "category":        category,
            "text":            original,
            "translated_text": trans,
            "formatted_text":  formatted,
            "location":        "west_bank" if is_about_west_bank(trans)
                               else ("gaza" if is_about_gaza(trans) else None)
        })
        print(f"📦 Message {m.id} enregistré ({category}) depuis [{chan}]")

    if is_similar_to_existing(formatted):
        print("Message ignoré: doublon")
        return
    previous_texts.append(formatted)
    transferred_ids.add(m.id)
    save_transferred_ids()
    save_content_texts()
    target = target_channel_west_bank if is_about_west_bank(trans) else target_channel_gaza
    try:
        await client.send_message(target, formatted)
        print(f"✅ Transféré vers {target}")
    except Exception as e:
        print(f"Erreur transfert: {e}")

# Analyse manuelle initiale
async def fetch_last_messages(limit=3):
    print(f"🔍 Analyse des {limit} derniers messages...")
    cutoff = datetime.now(timezone.utc) - timedelta(hours=8)
    for cid in source_channels_ids:
        try:
            ent = await client.get_entity(cid)
            async for m in client.iter_messages(ent, limit=limit):
                if m.date < cutoff: continue
                if not m.message or len(m.message.split()) < 4: continue
                fake = type('FakeEvent', (), {'message': m, 'chat': ent})
                await handler(fake)
        except Exception as e:
            print(f"Erreur analyse {cid}: {e}")

# Démarrage
if __name__ == "__main__":
    with client:
        print("🤖 Bot lancé. En écoute des nouveaux messages...")
        client.loop.run_until_complete(fetch_last_messages(limit=20))
        client.run_until_disconnected()
