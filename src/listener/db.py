"""
Módulo para gestionar la conexión y operaciones con MongoDB Atlas
"""
import os
from datetime import datetime
from typing import Dict, List, Optional
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDBManager:
    """Gestor de conexión y operaciones con MongoDB Atlas"""
    
    def __init__(self, mongo_uri: str, db_name: str):
        """
        Inicializa la conexión con MongoDB Atlas
        
        Args:
            mongo_uri: URI de conexión a MongoDB Atlas
            db_name: Nombre de la base de datos
        """
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.messages_collection: Optional[Collection] = None
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        
    def connect(self) -> bool:
        """
        Establece conexión con MongoDB Atlas
        
        Returns:
            bool: True si la conexión es exitosa, False en caso contrario
        """
        try:
            self.client = MongoClient(self.mongo_uri)
            # Verificar conexión
            self.client.admin.command('ismaster')
            self.db = self.client[self.db_name]
            self.messages_collection = self.db.messages
            logger.info(f"✅ Conectado exitosamente a MongoDB Atlas - DB: {self.db_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Error conectando a MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Cierra la conexión con MongoDB"""
        if self.client:
            self.client.close()
            logger.info("🔌 Desconectado de MongoDB Atlas")
    
    def insert_message(self, message_data: Dict) -> Optional[str]:
        """
        Inserta un mensaje en la colección
        
        Args:
            message_data: Diccionario con los datos del mensaje
            
        Returns:
            str: ID del documento insertado o None si hay error
        """
        try:
            # Agregar timestamp si no existe
            if 'timestamp' not in message_data:
                message_data['timestamp'] = datetime.utcnow()
            
            result = self.messages_collection.insert_one(message_data)
            logger.info(f"📝 Mensaje guardado con ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"❌ Error insertando mensaje: {e}")
            return None
    
    def create_indexes(self):
        """Crea índices para búsquedas eficientes"""
        try:
            # Índice por timestamp para consultas temporales
            self.messages_collection.create_index("timestamp")
            # Índice por chat_id para filtrar por chat
            self.messages_collection.create_index("chat_id")
            # Índice por sender_id para análisis de usuarios
            self.messages_collection.create_index("sender_id")
            # Índice compuesto para búsquedas avanzadas
            self.messages_collection.create_index([("chat_id", 1), ("timestamp", -1)])
            logger.info("📊 Índices creados exitosamente")
        except Exception as e:
            logger.error(f"❌ Error creando índices: {e}")
    
    def get_messages_count(self) -> int:
        """
        Obtiene el número total de mensajes almacenados
        
        Returns:
            int: Número de mensajes
        """
        try:
            return self.messages_collection.count_documents({})
        except Exception as e:
            logger.error(f"❌ Error obteniendo count: {e}")
            return 0
    
    def test_connection(self) -> bool:
        """
        Prueba la conexión insertando un documento de test
        
        Returns:
            bool: True si el test es exitoso
        """
        try:
            test_doc = {
                "test": True,
                "timestamp": datetime.utcnow(),
                "message": "Test de conexión"
            }
            result = self.messages_collection.insert_one(test_doc)
            # Eliminar el documento de test
            self.messages_collection.delete_one({"_id": result.inserted_id})
            logger.info("✅ Test de conexión exitoso")
            return True
        except Exception as e:
            logger.error(f"❌ Test de conexión falló: {e}")
            return False