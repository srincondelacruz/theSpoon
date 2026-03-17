import os
import re
from typing import Optional
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from dotenv import load_dotenv

load_dotenv()

CUSTOM_MODEL_ID = os.environ.get("AZURE_MODEL_ID", "ocr-4")


def find_price_in_text(text: str) -> Optional[float]:
    """Busca patrones de precios como '12€', '10.50€', '9,95€' en el texto."""
    pattern = r"(\d+[.,]?\d*)\s*€|€\s*(\d+[.,]?\d*)"
    match = re.search(pattern, text)
    if match:
        price_str = match.group(1) if match.group(1) else match.group(2)
        price_str = price_str.replace(',', '.')
        try:
            return float(price_str)
        except ValueError:
            return None
    return None


def _get_field_value(fields: dict, field_name: str) -> str:
    """Extrae valor string de un campo del modelo. Devuelve '' si no existe."""
    field = fields.get(field_name)
    if field is None:
        return ""
    return getattr(field, 'value_string', None) or ""


def extract_menu_from_image(image_bytes: bytes) -> dict:
    """
    Usa el modelo custom de Azure Document Intelligence (ocr-4).
    Identifica platos con el campo 'Nombre de plato' del modelo.
    Categoriza cada plato por proximidad espacial (coordenada X) al header de sección.
    Devuelve SOLO datos reales del modelo. Sin heurísticas, sin placeholders.
    """
    endpoint = os.environ.get("AZURE_VISION_ENDPOINT")
    key = os.environ.get("AZURE_VISION_KEY")

    if not endpoint or not key:
        raise ValueError("Faltan las credenciales de Azure (AZURE_VISION_ENDPOINT / AZURE_VISION_KEY)")

    client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    poller = client.begin_analyze_document(
        CUSTOM_MODEL_ID,
        body=image_bytes,
        content_type="application/octet-stream",
    )
    result = poller.result()

    # Extraer líneas con sus posiciones espaciales (polygon[0] = coordenada X)
    raw_text = ""
    all_lines = []
    if result.pages:
        for page in result.pages:
            for line in page.lines:
                raw_text += line.content + "\n"
                polygon = line.polygon or []
                x = polygon[0] if polygon else 0
                all_lines.append({"content": line.content, "x": x})
    raw_text = raw_text.strip()

    # Campos estructurados del modelo custom
    fields = {}
    if result.documents and len(result.documents) > 0:
        fields = result.documents[0].fields or {}

    nombre_content = _get_field_value(fields, "Nombre de plato")
    tipos_content = _get_field_value(fields, "Tipos de platos")

    # 1. Identificar headers de sección con su posición X
    sections = []
    if tipos_content:
        for line in all_lines:
            clean = line["content"].rstrip('. ')
            if clean and clean in tipos_content:
                sections.append({"name": line["content"], "x": line["x"]})

    # 2. Identificar platos (líneas que aparecen en "Nombre de plato")
    #    y asignar tipo por proximidad X al header de sección más cercano
    platos = []
    if nombre_content:
        for line in all_lines:
            if line["content"] in nombre_content:
                tipo = ""
                if sections:
                    closest = min(sections, key=lambda s: abs(s["x"] - line["x"]))
                    tipo = closest["name"]
                platos.append({
                    "tipo": tipo,
                    "nombre": line["content"],
                    "descripcion": "",
                    "suplemento": False,
                    "precio_suplemento": 0,
                })

    # Precio
    precio_str = _get_field_value(fields, "Precio")
    precio = find_price_in_text(precio_str) if precio_str else find_price_in_text(raw_text)

    return {
        "restaurante": {
            "nombre": _get_field_value(fields, "Nombre restaurante"),
            "direccion": _get_field_value(fields, "Direccion"),
            "telefono": _get_field_value(fields, "Numero de telefono"),
        },
        "ofertas": {
            "titulo": _get_field_value(fields, "Titulo"),
            "titulo_oferta": _get_field_value(fields, "Titulo oferta"),
            "fecha_oferta": _get_field_value(fields, "Fecha oferta"),
            "complementos": _get_field_value(fields, "Complementos"),
        },
        "platos": platos,
        "precio_general": precio,
        "raw_text": raw_text,
    }
