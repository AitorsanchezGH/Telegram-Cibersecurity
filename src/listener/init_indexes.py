"""
Script para inicializar la conexión con MongoDB y crear los índices necesarios
"""
from db import MongoDBManager
from config import MONGO_URI, MONGO_DB
import logging

def main():
    """Función principal para inicializar MongoDB"""
    print("🚀 Iniciando configuración de MongoDB Atlas...")
    
    # Crear instancia del gestor de DB
    db_manager = MongoDBManager(MONGO_URI, MONGO_DB)
    
    # Conectar
    if not db_manager.connect():
        print("❌ No se pudo conectar a MongoDB Atlas")
        return False
    
    # Probar conexión
    if not db_manager.test_connection():
        print("❌ Test de conexión falló")
        return False
    
    # Crear índices
    db_manager.create_indexes()
    
    # Mostrar información
    count = db_manager.get_messages_count()
    print(f"📊 Mensajes en la base de datos: {count}")
    
    # Desconectar
    db_manager.disconnect()
    
    print("✅ Configuración completada exitosamente")
    return True

if __name__ == "__main__":
    main()