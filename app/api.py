from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import traceback
from datetime import datetime
from typing import Optional
from datetime import datetime

# Ensure the scripts directory is in the path to import interprete_menu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.ocr_service import extract_menu_from_image
from app.services.weather_service import get_current_weather, get_context_date_info
import scripts.interprete_menu as interprete_menu
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
clasificador = hf_pipeline("zero-shot-classification", model=interprete_menu.MODELO_NLP)
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
        resultado = interprete_menu.ejecutar_prediccion_completa(
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

DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

def _get_temporada():
    month = datetime.now().month
    if month in [12, 1, 2]: return "invierno"
    if month in [3, 4, 5]: return "primavera"
    if month in [6, 7, 8]: return "verano"
    return "otoño"

@app.post("/api/predict_menu_full")
async def predict_menu_full(file: UploadFile = File(...)):
    """
    Endpoint principal unificado:
    OCR Azure (modelo custom) -> Datos estructurados reales -> Predicción ML
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    try:
        content = await file.read()
        menu_data = extract_menu_from_image(content)

        if not menu_data["raw_text"]:
            raise HTTPException(status_code=400, detail="El OCR no detectó ningún texto en la imagen.")

        # Parámetros ML auto-calculados
        dia_semana = DIAS_SEMANA[datetime.now().weekday()]
        temporada = _get_temporada()
        precio_final = menu_data["precio_general"] or 12.0
        plato_para_ia = menu_data["platos"][0]["nombre"] if menu_data["platos"] else ""

        resultado_ml = {}
        if plato_para_ia:
            resultado_ml = ejecutar_prediccion_completa(
                plato=plato_para_ia,
                dia_semana=dia_semana,
                lluvia=False,
                temperatura=20.0,
                precio_menu=precio_final,
                temporada=temporada,
                clasificador=clasificador
            )

        return {
            "menu": {
                "restaurante": menu_data["restaurante"],
                "ofertas": menu_data["ofertas"],
                "platos": menu_data["platos"],
                "precio_general": menu_data["precio_general"],
            },
            "prediccion": resultado_ml,
            "raw_ocr_text": menu_data["raw_text"],
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recalculate_prediction")
async def recalculate(
    plato: str = Form(...),
    precio: float = Form(12.5)
):
    """Permite recalcular el ML si el usuario edita el nombre del plato del OCR."""
    clima = get_current_weather()
    dia_semana, temporada = get_context_date_info()
    
    resultado_ml = interprete_menu.ejecutar_prediccion_completa(
        plato=plato,
        dia_semana=dia_semana,
        lluvia=clima["raining"],
        temperatura=clima["temp"],
        precio_menu=precio,
        temporada=temporada,
        clasificador=clasificador
    )
    
    nivel_afluencia = "Alta" if resultado_ml["raciones"] > 40 else "Media" if resultado_ml["raciones"] > 25 else "Baja"
    
    return {
        **resultado_ml,
        "influx_label": nivel_afluencia,
        "weather_desc": "Lluvia" if clima["raining"] else "Despejado"
    }
