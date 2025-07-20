from telethon.sync import TelegramClient

api_id = YOUR_API_ID
api_hash = 'YOUR_API_HASH'
session_name = 'session_translate'

with TelegramClient(session_name, api_id, api_hash) as client:
    username = 'ajmideast'  # ⚠️ Pas de https://
    try:
        entity = client.get_entity(username)
        print(f"✅ Channel ID: {entity.id}")
    except Exception as e:
        print(f"❌ Erreur : {e}")