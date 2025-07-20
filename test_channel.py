from telethon.sync import TelegramClient

api_id = 23811758
api_hash = 'cbfd3db91bd6b98fdcad644153fd7ccd'
session_name = 'session_channels'

target_channel = -1002544405911  # ← Le canal que TU veux viser

with TelegramClient(session_name, api_id, api_hash) as client:
    client.send_message(target_channel, "✅ Test de publication dans le bon canal")
    print("Message envoyé.")