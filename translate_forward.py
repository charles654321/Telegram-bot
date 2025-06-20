from telethon import TelegramClient, events
from googletrans import Translator
import traceback

# Tes identifiants API Telegram
api_id = 25668434
api_hash = '8ca8502ca239377bf945e89c62ad5f94'
session_name = 'session_translate'

# Chaînes sources à surveiller
source_channels = ['@hamza20300', '@osama1984osama', '@mumenjmmeqdad']

# ID numérique de ta chaîne cible (si privée)
target_channel = -1002629171243

# Initialisation des clients
client = TelegramClient(session_name, api_id, api_hash)
translator = Translator()

# 🔁 Récupérer les 10 derniers messages de chaque chaîne
async def get_last_messages():
    for channel in source_channels:
        print(f"📡 Récupération des 10 derniers messages de {channel}")
        try:
            async for message in client.iter_messages(channel, limit=10, reverse=True):
                original_text = message.raw_text.strip() if message.raw_text else ''
                translated = ''
                if original_text:
                    translated = translator.translate(original_text, src='ar', dest='en').text

                if message.media:
                    await client.send_file(
                        target_channel,
                        file=message.media,
                        caption=translated if translated else None
                    )
                    print("📤 Média ancien envoyé.")
                elif translated:
                    await client.send_message(target_channel, translated)
                    print(f"📤 Ancien message envoyé : {translated}")
                else:
                    print("ℹ️ Message sans texte ni média ignoré.")
        except Exception as e:
            print(f"❌ Erreur avec {channel} :")
            traceback.print_exc()

# 🎧 Gérer les nouveaux messages en temps réel
@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    print("📥 Nouveau message reçu")
    print(f"Texte brut : {event.raw_text}")
    print(f"Média ? {bool(event.media)}")
    try:
        original_text = event.raw_text.strip() if event.raw_text else ''
        translated = ''
        if original_text:
            translated = translator.translate(original_text, src='ar', dest='en').text

        if event.media:
            await client.send_file(
                target_channel,
                file=event.media,
                caption=translated if translated else None
            )
            print("📸 Média en direct envoyé.")
        elif translated:
            await client.send_message(target_channel, translated)
            print(f"✅ Message en direct traduit : {translated}")
        else:
            print("⚠️ Message vide ignoré.")
    except Exception as e:
        print("❌ Erreur en direct :")
        traceback.print_exc()

# 🚀 Lancer la récupération + l'écoute
async def main():
    await get_last_messages()
    print("✅ Lecture des anciens messages terminée. Le bot passe en mode écoute.")
    await client.run_until_disconnected()

# 🚀 Lancement principal
client.start()
client.loop.run_until_complete(main())
