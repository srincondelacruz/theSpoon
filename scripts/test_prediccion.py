"""
La Cuchara — Test de Predicción en Tiempo Real
===============================================
Simula una petición real que llegaría desde la App/Frontend:
carga el modelo entrenado y predice cuántos menús preparar
para un día concreto con condiciones específicas.
"""

import os                  # Para manejar rutas de archivos
import joblib              # Para cargar el modelo guardado
import pandas as pd        # Para crear el DataFrame de entrada

# ============================================================
# 1. CARGAR EL MODELO (Pipeline completo)
# ============================================================
# El archivo .pkl contiene el preprocesador + Random Forest empaquetados.
# Con una sola llamada a .predict(), el pipeline se encarga de:
#   1. Convertir las columnas categóricas en flags (One-Hot Encoding)
#   2. Pasar las flags al Random Forest para obtener la predicción
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELO_PATH = os.path.join(BASE_DIR, "models", "demand_predictor.pkl")

print("🧠 Cargando modelo desde:", MODELO_PATH)
pipeline = joblib.load(MODELO_PATH)                  # Cargamos el pipeline completo
print("   ✅ Modelo cargado correctamente\n")

# ============================================================
# 2. SIMULAR UNA PETICIÓN REAL (como si viniera de la App)
# ============================================================
# Creamos un DataFrame con exactamente las mismas columnas que usamos
# durante el entrenamiento. Esto es lo que enviaría el frontend:
#
#   "Oye modelo, mañana es viernes, va a llover, el restaurante
#    es de cocina Tradicional Española, hace 7°C, el menú cuesta
#    12.50€ y estamos en invierno. ¿Cuántos menús preparo?"

dia_simulado = pd.DataFrame([{
    "dia_semana":   "Viernes",                # Viernes → menos demanda de menú del día
    "tipo_cocina":  "Tradicional Española",   # Cocido, fabada... platos de cuchara
    "lluvia":       True,                     # Va a llover → la gente se queda más en casa
    "temperatura":  7.0,                      # 7°C → frío invernal en Madrid
    "precio_menu":  12.50,                    # Precio del menú del día
    "temporada":    "invierno",               # Temporada de invierno
}])

# ============================================================
# 3. PREDECIR
# ============================================================
# El pipeline recibe el DataFrame "crudo" (con texto) y lo transforma
# internamente antes de pasárselo al Random Forest. ¡Magia del Pipeline!
prediccion = pipeline.predict(dia_simulado)          # Devuelve un array con la predicción
raciones = int(round(prediccion[0]))                 # Redondeamos a número entero

# ============================================================
# 4. MOSTRAR EL RESULTADO (simulando la interfaz de la App)
# ============================================================
print("=" * 55)
print("  🥄  LA CUCHARA — Predicción de Demanda")
print("=" * 55)
print()
print("  📅 Día planificado:")
print(f"     → Día:         {dia_simulado['dia_semana'].iloc[0]}")
print(f"     → Temporada:   {dia_simulado['temporada'].iloc[0]}")
print()
print("  🍽️  Restaurante:")
print(f"     → Cocina:      {dia_simulado['tipo_cocina'].iloc[0]}")
print(f"     → Precio menú: {dia_simulado['precio_menu'].iloc[0]:.2f} €")
print()
print("  🌤️  Clima previsto:")
print(f"     → Temperatura: {dia_simulado['temperatura'].iloc[0]}°C")
print(f"     → Lluvia:      {'🌧️ Sí, llueve' if dia_simulado['lluvia'].iloc[0] else '☀️ No llueve'}")
print()
print("  ┌─────────────────────────────────────────────┐")
print(f"  │  📊 Raciones recomendadas a cocinar: {raciones:>4}    │")
print("  └─────────────────────────────────────────────┘")
print()
print(f"  💡 El modelo recomienda preparar ~{raciones} menús.")
print(f"     Con este dato, el chef puede planificar las compras")
print(f"     y minimizar el desperdicio alimentario.")
print()
print("  ✨ ¡Predicción completada!")
