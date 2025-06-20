from telethon import TelegramClient, events
from translate import Translator

# Tes identifiants API Telegram
api_id = 25668434
api_hash = '8ca8502ca239377bf945e89c62ad5f94'

session_name = 'session_translate'

source_channels = ['@hamza20300', '@osama1984osama', '@mumenjmmeqdad']
target_channel = -1002629171243

client = TelegramClient(session_name, api_id, api_hash)
translator = Translator(to_lang="en", from_lang="ar")

@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    try:
        original_text = event.raw_text.strip() if event.raw_text else ''
        translated = ''

        if original_text:
            translated = translator.translate(original_text)

        if event.media:
            await client.send_file(
                target_channel,
                file=event.media,
                caption=translated if translated else None
            )
            print("📸 Média envoyé avec traduction.")

        elif translated:
            await client.send_message(target_channel, translated)
            print(f"✅ Texte traduit et envoyé : {translated}")

        else:
            print("⚠️ Message vide ignoré.")

    except Exception as e:
        print(f"❌ Erreur lors du traitement : {e}")

client.start()
print("🤖 Le bot fonctionne maintenant (mode invisible).")
client.run_until_disconnected()