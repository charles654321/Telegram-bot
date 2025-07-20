from telethon.sync import TelegramClient
from telethon.tl.types import Channel

# Remplace par tes infos
api_id = 23811758
api_hash = 'cbfd3db91bd6b98fdcad644153fd7ccd'
session_name = 'session_channels'

with TelegramClient(session_name, api_id, api_hash) as client:
    print("📢 Vos chaînes Telegram (où vous êtes membre) :\n")
    for dialog in client.iter_dialogs():
        entity = dialog.entity
        if isinstance(entity, Channel) and entity.broadcast:  # broadcast = chaîne (pas groupe)
            print(f"Nom : {dialog.name}")
            print(f"ID   : {entity.id}")
            print("-" * 40)