
#Utilidades para formatear y procesar mensajes de Telegram

import re
from datetime import datetime
from typing import Dict, List, Optional
from telethon.tl.types import MessageEntityUrl, MessageEntityTextUrl

def extract_urls_from_text(text: str) -> List[str]:
    """
    Extrae URLs del texto usando regex
    
    Args:
        text: Texto del mensaje
        
    Returns:
        List[str]: Lista de URLs encontradas
    """
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)

def format_message_for_db(event) -> Dict:
    """
    Convierte un evento de Telegram en el formato para MongoDB
    
    Args:
        event: Evento de Telegram (NewMessage)
        
    Returns:
        Dict: Datos formateados para insertar en MongoDB
    """
    # Información básica del mensaje
    message_data = {
        # IDs únicos
        "message_id": event.message.id,
        "chat_id": event.chat_id,
        "sender_id": event.sender_id,
        
        # Contenido
        "text": event.raw_text or "",
        "date": event.message.date,
        "timestamp": datetime.utcnow(),  # Timestamp de cuando lo procesamos
        
        # Metadatos para análisis de ciberseguridad
        "urls": extract_urls_from_text(event.raw_text or ""),
        "has_urls": bool(extract_urls_from_text(event.raw_text or "")),
        "message_length": len(event.raw_text or ""),
        
        # Información del chat
        "chat_title": None,
        "chat_type": None,
        "chat_username": None,
        
        # Información del remitente
        "sender_username": None,
        "sender_first_name": None,
        "sender_last_name": None,
        "sender_phone": None,
        
        # Análisis futuro (inicialmente vacío)
        "analysis": {
            "is_spam": None,
            "is_phishing": None,
            "risk_score": None,
            "keywords_detected": [],
            "analysis_timestamp": None
        },
        
        # Metadatos adicionales
        "has_media": bool(event.message.media),
        "media_type": None, 
        "reply_to_msg_id": event.message.reply_to_msg_id,
        "forward_info": None
    }
    
    # Obtener información del chat si está disponible
    if hasattr(event, 'chat') and event.chat:
        chat = event.chat
        message_data["chat_title"] = getattr(chat, 'title', None)
        message_data["chat_username"] = getattr(chat, 'username', None)
        
        # Determinar tipo de chat
        if hasattr(chat, 'broadcast'):
            message_data["chat_type"] = "channel" if chat.broadcast else "group"
        else:
            message_data["chat_type"] = "private"
    
    # Obtener información del remitente si está disponible
    if hasattr(event, 'sender') and event.sender:
        sender = event.sender
        message_data["sender_username"] = getattr(sender, 'username', None)
        message_data["sender_first_name"] = getattr(sender, 'first_name', None)
        message_data["sender_last_name"] = getattr(sender, 'last_name', None)
        message_data["sender_phone"] = getattr(sender, 'phone', None)
    
    # Información sobre medios
    if event.message.media:
        media_type = type(event.message.media).__name__
        message_data["media_type"] = media_type
    
    # Información de reenvío
    if event.message.forward:
        forward_info = event.message.forward
        message_data["forward_info"] = {
            "date": forward_info.date,
            "from_id": getattr(forward_info, 'from_id', None),
            "from_name": getattr(forward_info, 'from_name', None)
        }
    
    return message_data

def is_suspicious_message(message_data: Dict) -> Dict:
    """
    Análisis básico para detectar mensajes sospechosos
    
    Args:
        message_data: Datos del mensaje formateados
        
    Returns:
        Dict: Resultados del análisis
    """
    analysis = {
        "is_suspicious": False,
        "reasons": [],
        "risk_score": 0
    }
    
    text = message_data.get("text", "").lower()
    urls = message_data.get("urls", [])
    
    # Palabras clave sospechosas (básico)
    suspicious_keywords = [
        "premio", "ganador", "felicidades", "click aqui", "urgente",
        "bitcoin", "crypto", "inversion", "dinero facil", "descarga",
        "verificar cuenta", "suspendido", "bloquear", "confirmar"
    ]
    
    found_keywords = [kw for kw in suspicious_keywords if kw in text]
    
    if found_keywords:
        analysis["is_suspicious"] = True
        analysis["reasons"].append(f"Palabras sospechosas: {', '.join(found_keywords)}")
        analysis["risk_score"] += len(found_keywords) * 10
    
    # URLs sospechosas
    if urls:
        analysis["reasons"].append(f"Contiene {len(urls)} URL(s)")
        analysis["risk_score"] += len(urls) * 5
        
        # URLs con acortadores comunes
        suspicious_domains = ["bit.ly", "tinyurl.com", "t.co", "goo.gl"]
        for url in urls:
            if any(domain in url for domain in suspicious_domains):
                analysis["is_suspicious"] = True
                analysis["reasons"].append("URL acortada detectada")
                analysis["risk_score"] += 15
    
    # Mensajes muy largos o muy cortos con URLs
    if urls and (len(text) < 50 or len(text) > 1000):
        analysis["is_suspicious"] = True
        analysis["reasons"].append("Longitud sospechosa con URLs")
        analysis["risk_score"] += 10
    
    return analysis