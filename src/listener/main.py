from telethon import TelegramClient, events
from config import API_ID, API_HASH, SESSION_NAME

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    print(f"[{event.chat_id}] {event.sender_id}: {event.raw_text}")

def main():
    print(">> Listener iniciado. Ctrl+C para salir.")
    with client:
        client.run_until_disconnected()

if __name__ == "__main__":
    main()
