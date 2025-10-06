import os
from dotenv import load_dotenv

load_dotenv()  # carga el archivo .env

# Configuración de Telegram
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME", "tfg_session")

# Configuración de MongoDB Atlas
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "TFG")