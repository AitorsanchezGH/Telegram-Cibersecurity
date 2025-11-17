
from datetime import datetime
from typing import Dict

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

def analyze_message(message_data: Dict) -> Dict:
    """
    Aplica el análisis basado en reglas a un mensaje y devuelve
    un diccionario unificado de análisis.
    """
    base = is_suspicious_message(message_data)
    
    label = "spam" if base["is_suspicious"] else "no_spam"
    
    analysis = {
        "label": label,
        "is_suspicious": base["is_suspicious"],
        "risk_score": base["risk_score"],
        "reasons": base["reasons"],
        "probabilities": None,  # futuro modelo ML
        "analysis_timestamp": datetime.now()
    }
    
    return analysis