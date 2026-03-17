from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
from typing import Optional

# Ensure the scripts directory is in the path to import interprete_menu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.interprete_menu import ejecutar_prediccion_completa, MODELO_NLP
from app.services.ocr_service import extract_text_from_image
from transformers import pipeline as hf_pipeline

app = FastAPI(title="La Cuchara API - OCR & ML")

# Enable CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to the localhost or domain URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Starting to load the ML models. This might take a bit on first run...")
clasificador = hf_pipeline("zero-shot-classification", model=MODELO_NLP)
print("Models loaded successfully.")

def obtener_mejor_plato_para_clase(texto_ocr: str) -> str:
    """
    Intenta saltar encabezados como 'PRIMEROS:' o líneas con el precio 
    para encontrar el nombre real del primer plato.
    """
    lineas = texto_ocr.split('\n')
    # Palabras que suelen ser encabezados y no platos
    keywords_a_ignorar = ["primeros", "segundos", "postres", "bebidas", "menú", "menu"]
    
    for linea in lineas:
        clean = linea.replace('-', '').strip()
        if not clean: continue
        
        # Si la línea contiene el precio (ej: 11€), intentamos saltarla para clasificar
        if "€" in clean or any(char.isdigit() for char in clean if char not in "0123456789"): 
             # Si tiene dígitos pero no es un nombre de plato (muy corto o con €)
             if len(clean) < 10 or "€" in clean:
                 continue
        
        # Si la línea es un encabezado puro
        if clean.lower().strip(': ') in keywords_a_ignorar:
            continue
            
        if len(clean) > 3:
            return clean
            
    return lineas[0] if lineas else ""


class PlatosRequest(BaseModel):
    platos_texto: str
    dia_semana: str
    lluvia: bool
    temperatura: float
    precio_menu: float
    temporada: str

@app.post("/api/ocr")
async def ocr_image(file: UploadFile = File(...)):
    """
    Endpoint that simulates Azure AI OCR for demonstration.
    In real production, this would send `file` to Azure Document Intelligence
    and return the text. Here we provide a mock realistic response to use directly.
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    # MOCK OCR RESPONSE: In reality you would send the image bytes to Azure
    # content = await file.read()
    # ocr_result = call_azure_document_intelligence(content)
    
    return {
        "text_extracted": "- Risotto trufado con boletus\n- Tacos de cochinita pibil\n- Tiramisú de matcha",
        "mock_note": "This is a mock OCR output. Real implementation requires Azure API keys."
    }

@app.post("/api/predict_menu")
def predict_menu(request: PlatosRequest):
    """
    Receives normalized text (platos), categorizes it and returns ML demand predictions.
    """
    # Simply using the first dish of the list for category for this array for simplicity,
    # or treating the whole string for the DeBerta Model
    
    # We take the first dish ignoring hyphens for the model, or just use the raw text
    primer_plato = request.platos_texto.split('\n')[0].replace('-', '').strip()
    if not primer_plato:
        primer_plato = request.platos_texto
        
    try:
        resultado = ejecutar_prediccion_completa(
            plato=primer_plato,
            dia_semana=request.dia_semana,
            lluvia=request.lluvia,
            temperatura=request.temperatura,
            precio_menu=request.precio_menu,
            temporada=request.temporada,
            clasificador=clasificador
        )
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict_menu_full")
async def predict_menu_full(
    file: UploadFile = File(...),
    dia_semana: str = Form("Lunes"),
    lluvia: bool = Form(False),
    temperatura: float = Form(20.0),
    precio_menu: float = Form(12.5),
    temporada: Optional[str] = Form("primavera")
):
    """
    Endpoint principal unificado: 
    OCR Azure -> Parsing Estructurado -> Predicción ML
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
        
    try:
        # 1. OCR (Azure API)
        content = await file.read()
        ocr_text, precio_detectado = extract_text_from_image(content)
        
        if not ocr_text:
            raise HTTPException(status_code=400, detail="El OCR no detectó ningún texto en la imagen.")
            
        precio_final = precio_detectado if precio_detectado is not None else precio_menu
        
        # 2. Parsing Estructurado del texto
        lineas = [l.strip() for l in ocr_text.split('\n') if l.strip()]
        nombre_restaurante = lineas[0] if lineas else "Restaurante Desconocido"
        plato_para_ia = obtener_mejor_plato_para_clase(ocr_text)
        
        menu_estructurado = {
            "restaurante": {
                "nombre": nombre_restaurante,
                "direccion": "Consultar en mapa...", 
                "telefono": "Añadir teléfono..."
            },
            "ofertas": {
                "titulo": "Menú del día",
                "titulo_oferta": "Oferta Especial",
                "fecha_oferta": dia_semana,
                "complementos": "Pan, bebida y café incluidos"
            },
            "platos": [
                {"tipo": "1º Plato", "nombre": plato_para_ia, "descripcion": "Extraído por OCR", "suplemento": False, "precio_suplemento": 0},
                {"tipo": "2º Plato", "nombre": "Siguiente plato detectado...", "descripcion": "", "suplemento": False, "precio_suplemento": 0}
            ],
            "precio_general": precio_final
        }
            
        # 3. Predicción de demanda (ML)
        resultado_ml = ejecutar_prediccion_completa(
            plato=plato_para_ia,
            dia_semana=dia_semana,
            lluvia=lluvia,
            temperatura=temperatura,
            precio_menu=precio_final,
            temporada=temporada,
            clasificador=clasificador
        )
        
        return {
            "menu": menu_estructurado,
            "prediccion": resultado_ml,
            "raw_ocr_text": ocr_text
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
