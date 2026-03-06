"""
La Cuchara — Intérprete Híbrido de Menú (Diccionario + NLP)
============================================================
Arquitectura de dos capas para clasificar platos:

  CAPA 1 — Diccionario de palabras clave (rápido, 100% preciso)
  CAPA 2 — NLP Zero-Shot con mDeBERTa (fallback inteligente)

Si el plato contiene una palabra del diccionario → se usa la Capa 1.
Si no se encuentra ninguna coincidencia → se activa la Capa 2 (NLP).
"""

import os              # Para manejar rutas de archivos
import joblib          # Para cargar el modelo de demanda (.pkl)
import pandas as pd    # Para crear el DataFrame de entrada

# Importamos el pipeline de Hugging Face Transformers
from transformers import pipeline as hf_pipeline


# ============================================================
# CONFIGURACIÓN
# ============================================================
MODELO_NLP = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"

# ============================================================
# CAPA 1: Diccionario de palabras clave → tipo_cocina
# ============================================================
# Cada tipo de cocina tiene una lista de palabras INCONFUNDIBLES.
# Si alguna aparece en el nombre del plato, sabemos la categoría al 100%.
DICCIONARIO_COCINAS = {
    "Tradicional Española": [
        "cocido", "fabada", "lentejas", "garbanzos", "potaje",
        "puchero", "callos", "tortilla", "croquetas", "migas",
        "gazpacho", "salmorejo", "albóndigas", "judías", "menestra",
        "estofado", "rabo de toro", "secreto ibérico", "lomo",
        "sopa castellana", "pimientos de padrón", "patatas bravas",
        "ensaladilla rusa", "merluza", "cachopo",
    ],
    "Italiana": [
        "pasta", "pizza", "lasaña", "risotto", "ravioli",
        "ñoquis", "carbonara", "boloñesa", "penne", "linguine",
        "bruschetta", "caprese", "ossobuco", "scaloppine",
        "minestrone", "antipasto", "parmesano", "gnocchi",
        "tagliatelle", "focaccia", "calzone", "prosciutto",
        "tiramisú", "panna cotta",
    ],
    "Asiática": [
        "sushi", "ramen", "wok", "gyozas", "teriyaki",
        "pad thai", "miso", "soja", "curry", "dim sum",
        "noodles", "edamame", "bibimbap", "yakisoba",
        "pho", "tom yum", "wonton", "kung pao", "tempura",
        "sashimi", "udon", "dumpling", "kimchi", "satay",
        "oriental", "thai", "vietnamita", "pekinés",
    ],
    "Mexicana": [
        "taco", "tacos", "burrito", "enchilada", "enchiladas",
        "quesadilla", "quesadillas", "nacho", "nachos",
        "guacamole", "fajita", "fajitas", "pozole", "mole",
        "chilaquiles", "tamales", "tostadas", "elote",
        "cochinita", "pibil", "habanero", "jalapeño",
        "chimichanga", "churro", "tortilla mexicana",
    ],
    "Vegetariana": [
        "vegano", "vegana", "vegetal", "buddha bowl",
        "jackfruit", "tempeh", "seitan", "tofu",
        "quinoa", "ensalada power", "bowl hawaiano",
    ],
    "Arrocería": [
        "paella", "arroz caldoso", "arroz negro", "fideuá",
        "arroz al horno", "arroz a banda", "arroz meloso",
    ],
    "Asador": [
        "chuletón", "cochinillo", "lechazo", "entrecot",
        "brasa", "asado", "chuletas", "codillo",
        "solomillo", "parrillada", "bbq", "costillas",
    ],
    "Marisquería": [
        "marisco", "gambas", "langostinos", "mejillones",
        "almejas", "pulpo", "navajas", "vieiras", "bogavante",
        "camarón", "salpicón", "zarzuela", "rape",
    ],
}

# Palabras clave para detectar platos FRÍOS (regla especial)
PALABRAS_PLATO_FRIO = ["helada", "fría", "frío", "gazpacho", "salmorejo"]

# Etiquetas para el NLP (Capa 2 — fallback)
ETIQUETAS_NLP = ["española", "asiática", "italiana", "mexicana", "vegetariana o saludable"]

# Mapeo NLP → tipo_cocina
MAPEO_NLP = {
    "española":                  "Tradicional Española",
    "asiática":                  "Asiática",
    "italiana":                  "Italiana",
    "mexicana":                  "Mexicana",
    "vegetariana o saludable":   "Vegetariana",
}


# ============================================================
# FUNCIÓN PRINCIPAL: Categorizar plato (Híbrida)
# ============================================================
def categorizar_plato(texto: str, clasificador) -> dict:
    """
    Clasifica un plato en tipo de cocina usando una arquitectura híbrida:

      1. REGLA: detecta platos fríos (gazpacho, crema helada...)
      2. CAPA 1 (Diccionario): busca palabras clave inconfundibles
      3. CAPA 2 (NLP): si no hay match, usa zero-shot classification

    Returns:
        Diccionario con: etiqueta, confianza, tipo_cocina, temporada_sugerida, metodo
    """
    texto_lower = texto.lower()

    # ── REGLA ESPECIAL: platos fríos españoles ──────────────
    # Si detectamos palabras como 'helada', 'gazpacho', 'salmorejo',
    # clasificamos directamente sin NLP ni diccionario.
    for palabra in PALABRAS_PLATO_FRIO:
        if palabra in texto_lower:
            return {
                "etiqueta":           f"plato frío ('{palabra}')",
                "confianza":          1.0,
                "tipo_cocina":        "Tradicional Española",
                "temporada_sugerida": "primavera",
                "metodo":             "🛡️ REGLA",
            }

    # ── CAPA 1: Diccionario de palabras clave ───────────────
    # Recorremos cada cocina y sus palabras clave.
    # Si encontramos una coincidencia, devolvemos al instante.
    for cocina, palabras in DICCIONARIO_COCINAS.items():
        for palabra in palabras:
            if palabra in texto_lower:
                return {
                    "etiqueta":           f"'{palabra}'",
                    "confianza":          1.0,
                    "tipo_cocina":        cocina,
                    "temporada_sugerida": None,
                    "metodo":             "📖 Diccionario",
                }

    # ── CAPA 2: NLP Zero-Shot (fallback) ────────────────────
    # Si ninguna palabra del diccionario coincidió, usamos mDeBERTa.
    # El modelo interpreta semánticamente el nombre del plato.
    resultado = clasificador(
        texto,
        candidate_labels=ETIQUETAS_NLP,
        hypothesis_template="Este plato es una receta típica de la gastronomía {}.",
    )

    etiqueta = resultado["labels"][0]
    confianza = resultado["scores"][0]

    tipo_cocina = MAPEO_NLP.get(etiqueta, "Tradicional Española")

    return {
        "etiqueta":           etiqueta,
        "confianza":          confianza,
        "tipo_cocina":        tipo_cocina,
        "temporada_sugerida": None,
        "metodo":             "🤖 NLP",
    }


# ============================================================
# Predicción completa (categorización + modelo de demanda)
# ============================================================
def ejecutar_prediccion_completa(
    plato: str,
    dia_semana: str,
    lluvia: bool,
    temperatura: float,
    precio_menu: float,
    temporada: str,
    clasificador,
) -> dict:
    """Flujo end-to-end: categoriza el plato + predice raciones."""

    # Paso 1: Categorizar con el sistema híbrido
    resultado_cat = categorizar_plato(plato, clasificador)
    tipo_cocina = resultado_cat["tipo_cocina"]

    # Si hay temporada sugerida (regla de platos fríos) y no se proporcionó una
    if resultado_cat["temporada_sugerida"] and temporada is None:
        temporada = resultado_cat["temporada_sugerida"]

    # Paso 2: Cargar modelo de demanda
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    modelo_path = os.path.join(base_dir, "models", "demand_predictor.pkl")
    pipeline_ml = joblib.load(modelo_path)

    # Paso 3: DataFrame con las columnas exactas del entrenamiento
    datos_entrada = pd.DataFrame([{
        "dia_semana":  dia_semana,
        "tipo_cocina": tipo_cocina,
        "lluvia":      lluvia,
        "temperatura": temperatura,
        "precio_menu": precio_menu,
        "temporada":   temporada,
    }])

    # Paso 4: Predecir
    prediccion = pipeline_ml.predict(datos_entrada)
    raciones = int(round(prediccion[0]))

    return {
        "plato":        plato,
        "etiqueta":     resultado_cat["etiqueta"],
        "confianza":    resultado_cat["confianza"],
        "tipo_cocina":  tipo_cocina,
        "metodo":       resultado_cat["metodo"],
        "dia_semana":   dia_semana,
        "lluvia":       lluvia,
        "temperatura":  temperatura,
        "precio_menu":  precio_menu,
        "temporada":    temporada,
        "raciones":     raciones,
    }


# ============================================================
# STRESS TEST
# ============================================================
def main():
    print("=" * 62)
    print("  🥄  LA CUCHARA — Intérprete HÍBRIDO (Diccionario + NLP)")
    print("=" * 62)

    # Inicializamos el modelo NLP (solo se usa si la Capa 1 falla)
    print("\n  🤖 Cargando modelo NLP (fallback)...")
    clasificador = hf_pipeline(
        "zero-shot-classification",
        model=MODELO_NLP,
    )
    print("  ✅ Modelo cargado\n")

    # Escenarios: mezcla de platos fáciles (diccionario) y difíciles (NLP)
    escenarios = [
        {   # Diccionario: 'cocido' → Tradicional Española
            "plato":       "Cocido de la abuela humeante",
            "dia_semana":  "Lunes",
            "lluvia":      True,
            "temperatura": 4.0,
            "precio_menu": 12.50,
            "temporada":   "invierno",
        },
        {   # Diccionario: 'oriental' → Asiática
            "plato":       "Fideos orientales con cerdo y jengibre",
            "dia_semana":  "Martes",
            "lluvia":      False,
            "temperatura": 16.0,
            "precio_menu": 11.00,
            "temporada":   "otoño",
        },
        {   # REGLA: 'helada' → Tradicional Española (plato frío)
            "plato":       "Crema helada de tomate con albahaca",
            "dia_semana":  "Jueves",
            "lluvia":      False,
            "temperatura": 28.0,
            "precio_menu": 13.00,
            "temporada":   "primavera",
        },
        {   # Diccionario: 'cochinita' / 'pibil' / 'habanero' → Mexicana
            "plato":       "Tacos de cochinita pibil con habanero",
            "dia_semana":  "Miércoles",
            "lluvia":      False,
            "temperatura": 18.0,
            "precio_menu": 11.00,
            "temporada":   "otoño",
        },
        {   # Diccionario: 'risotto' → Italiana
            "plato":       "Risotto trufado con boletus y parmesano",
            "dia_semana":  "Viernes",
            "lluvia":      True,
            "temperatura": 10.0,
            "precio_menu": 14.00,
            "temporada":   "invierno",
        },
        {   # Diccionario: 'tofu' + 'edamame' → Vegetariana
            "plato":       "Bowl de quinoa con tofu y edamame",
            "dia_semana":  "Lunes",
            "lluvia":      False,
            "temperatura": 22.0,
            "precio_menu": 12.00,
            "temporada":   "primavera",
        },
        {   # NLP: plato inventado sin palabras clave → fallback al NLP
            "plato":       "Estofado campesino con hierbas del monte",
            "dia_semana":  "Jueves",
            "lluvia":      True,
            "temperatura": 8.0,
            "precio_menu": 12.00,
            "temporada":   "invierno",
        },
        {   # NLP: plato exótico sin keywords → fallback al NLP
            "plato":       "Cuscús real con cordero y dátiles",
            "dia_semana":  "Martes",
            "lluvia":      False,
            "temperatura": 20.0,
            "precio_menu": 14.00,
            "temporada":   "primavera",
        },
    ]

    # Tabla resumen
    print("  ┌─────┬────────────────────────────────────────┬──────────────────────┬────────────┬──────────┐")
    print("  │  #  │ Plato                                  │ Tipo cocina          │ Método     │ Raciones │")
    print("  ├─────┼────────────────────────────────────────┼──────────────────────┼────────────┼──────────┤")

    for i, escenario in enumerate(escenarios, 1):
        resultado = ejecutar_prediccion_completa(
            clasificador=clasificador,
            **escenario,
        )

        # Formateo de la confianza según el método
        if resultado["confianza"] == 1.0:
            conf_str = "100%"
        else:
            conf_str = f"{resultado['confianza']:.0%}"

        plato_corto = resultado["plato"][:38].ljust(38)
        cocina_str = resultado["tipo_cocina"][:20].ljust(20)
        metodo_str = resultado["metodo"][:10].ljust(10)

        print(f"  │ {i:>2}  │ {plato_corto} │ {cocina_str} │ {metodo_str} │ {resultado['raciones']:>4}     │")

    print("  └─────┴────────────────────────────────────────┴──────────────────────┴────────────┴──────────┘")

    # Detalle de cada escenario
    print("\n" + "─" * 62)
    print("  � DETALLE POR ESCENARIO")
    print("─" * 62)

    for i, escenario in enumerate(escenarios, 1):
        resultado = ejecutar_prediccion_completa(
            clasificador=clasificador,
            **escenario,
        )

        if resultado["confianza"] == 1.0:
            conf_str = "100%"
        else:
            conf_str = f"{resultado['confianza']:.1%}"

        barra_len = 20
        llenos = int(resultado["confianza"] * barra_len)
        barra = "▓" * llenos + "░" * (barra_len - llenos)

        print(f"\n  ─── Escenario {i} ─────────────────────────────────")
        print(f"  📖 Plato:         {resultado['plato']}")
        print(f"  🔍 Método:        {resultado['metodo']}")
        print(f"  🏷️  Match:         {resultado['etiqueta']}")
        print(f"  📊 Confianza:     [{barra}] {conf_str}")
        print(f"  🍽️  Tipo cocina:   {resultado['tipo_cocina']}")
        print(f"  🔮 Raciones:      {resultado['raciones']}")

    print("\n" + "=" * 62)
    print("  ✨ ¡Stress test híbrido completado con éxito!")
    print("=" * 62)


if __name__ == "__main__":
    main()
