from telethon import TelegramClient, events
from config import API_ID, API_HASH, SESSION_NAME

# Creamos el cliente de Telegram con tus credenciales
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# Definimos un handler (función) que se ejecuta cada vez que entra un mensaje nuevo
@client.on(events.NewMessage)
async def handler(event):
    print(f"[{event.chat_id}] {event.sender_id}: {event.raw_text}")

def main():
    print(">> Listener iniciado. Ctrl+C para salir.")
    with client:
        client.run_until_disconnected()

if __name__ == "__main__":
    main()
