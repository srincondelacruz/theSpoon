import os
import re
from typing import Optional
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from dotenv import load_dotenv

# Cargar variables de entorno (AZURE_VISION_ENDPOINT y AZURE_VISION_KEY)
load_dotenv()

def find_price_in_text(text: str) -> Optional[float]:
    """
    Busca patrones de precios como '12€', '10.50€', '9,95€' en el texto.
    Devuelve el primer precio encontrado como float.
    """
    # Expresión regular para capturar números seguidos o precedidos de €
    # Captura: 11, 11.50, 11,50 etc.
    pattern = r"(\d+[.,]?\d*)\s*€|€\s*(\d+[.,]?\d*)"
    match = re.search(pattern, text)
    
    if match:
        price_str = match.group(1) if match.group(1) else match.group(2)
        # Normalizar coma a punto para convertir a float
        price_str = price_str.replace(',', '.')
        try:
            return float(price_str)
        except ValueError:
            return None
    return None

def extract_text_from_image(image_bytes: bytes) -> tuple:
    """
    Toma los bytes de una imagen y usa Azure Document Intelligence.
    Returns:
        tuple: (extracted_text, detected_price)
    """
    endpoint = os.environ.get("AZURE_VISION_ENDPOINT")
    key = os.environ.get("AZURE_VISION_KEY")
    
    if not endpoint or not key:
        raise ValueError("Faltan las credenciales de Azure...")

    client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    poller = client.begin_analyze_document(
        "prebuilt-read", 
        body=image_bytes,
        content_type="application/octet-stream"
    )
    result = poller.result()
    
    extracted_text = ""
    if result.pages:
        for page in result.pages:
            for line in page.lines:
                extracted_text += line.content + "\n"
                
    text_clean = extracted_text.strip()
    price = find_price_in_text(text_clean)
    
    return text_clean, price

