from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Ensure the scripts directory is in the path to import interprete_menu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.interprete_menu import ejecutar_prediccion_completa, MODELO_NLP
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
