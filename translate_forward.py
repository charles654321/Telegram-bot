from telethon import TelegramClient, events
from googletrans import Translator

# Tes identifiants API Telegram
api_id = 25668434   # <-- remplace avec le tien
api_hash = '8ca8502ca239377bf945e89c62ad5f94'  # <-- remplace avec le tien

# Session unique pour ce projet
session_name = 'session_translate'

# Chaînes sources en arabe (publiques)
source_channels = ['@hamza20300', '@osama1984osama', '@mumenjmmeqdad']  # remplace-les

# Chaîne cible (la tienne)
target_channel = -1002629171243

# Initialisation
client = TelegramClient(session_name, api_id, api_hash)
translator = Translator()

@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    try:
        # Traduire le texte s'il existe
        original_text = event.raw_text.strip()
        translated = ''
        if original_text:
            translated = translator.translate(original_text, src='ar', dest='en').text

        # Cas 1 : message avec média (photo, vidéo, etc.)
        if event.media:
            await client.send_file(
                target_channel,
                file=event.media,
                caption=translated if translated else None
            )
            print("📸 Média envoyé avec traduction.")

        # Cas 2 : message texte seul (pas de média)
        elif translated:
            await client.send_message(target_channel, translated)
            print(f"✅ Texte traduit et envoyé : {translated}")

        # Cas 3 : ni texte ni média → ne rien faire
        else:
            print("⚠️ Message vide ignoré.")

    except Exception as e:
        print(f"❌ Erreur lors du traitement : {e}")

client.start()
print("🤖 Le bot fonctionne maintenant (mode invisible).")
client.run_until_disconnected()
