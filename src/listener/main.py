from telethon import TelegramClient, events
from config import API_ID, API_HASH, SESSION_NAME, MONGO_URI, MONGO_DB
from db import MongoDBManager
from message_utils import format_message_for_db, is_suspicious_message
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Creamos el cliente de Telegram con tus credenciales
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# Inicializar gestor de base de datos
db_manager = MongoDBManager(MONGO_URI, MONGO_DB)

# Definimos un handler (función) que se ejecuta cada vez que entra un mensaje nuevo
@client.on(events.NewMessage)
async def handler(event):
    try:
        # Mostrar mensaje en consola (como antes)
        print(f"[{event.chat_id}] {event.sender_id}: {event.raw_text}")
        
        # Formatear mensaje para la base de datos
        message_data = format_message_for_db(event)
        
        # Realizar análisis básico
        analysis = is_suspicious_message(message_data)
        message_data["analysis"].update(analysis)
        
        # Guardar en MongoDB
        message_id = db_manager.insert_message(message_data)
        
        # Log adicional para mensajes sospechosos
        if analysis.get("is_suspicious"):
            logger.warning(f"⚠️  MENSAJE SOSPECHOSO detectado - ID: {message_id}")
            logger.warning(f"    Razones: {', '.join(analysis['reasons'])}")
            logger.warning(f"    Risk Score: {analysis['risk_score']}")
            
    except Exception as e:
        logger.error(f"❌ Error procesando mensaje: {e}")

def main():
    print("🚀 Iniciando Telegram Cybersecurity Listener...")
    
    # Conectar a MongoDB
    if not db_manager.connect():
        logger.error("❌ No se pudo conectar a MongoDB Atlas. Abortando...")
        return
    
    # Crear índices si es necesario
    db_manager.create_indexes()
    
    # Mostrar estadísticas iniciales
    initial_count = db_manager.get_messages_count()
    logger.info(f"📊 Mensajes en la base de datos: {initial_count}")
    
    print(">> Listener iniciado. Ctrl+C para salir.")
    
    try:
        with client:
            client.run_until_disconnected()
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo listener...")
    except Exception as e:
        logger.error(f"❌ Error en el listener: {e}")
    finally:
        # Mostrar estadísticas finales
        final_count = db_manager.get_messages_count()
        messages_processed = final_count - initial_count
        logger.info(f"📈 Mensajes procesados en esta sesión: {messages_processed}")
        logger.info(f"📊 Total mensajes en la base de datos: {final_count}")
        
        # Desconectar de MongoDB
        db_manager.disconnect()
        print("👋 ¡Hasta luego!")

if __name__ == "__main__":
    main()
