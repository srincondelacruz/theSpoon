# 🥄 La Cuchara

**Sistema inteligente de predicción de demanda para restaurantes en Azca, Madrid.**

La Cuchara permite a los restaurantes de la zona de Azca anticipar cuántos menús del día preparar cada jornada, reduciendo el **desperdicio alimentario** y optimizando las compras de materia prima. Combina datos históricos de ventas, factores climáticos y un modelo de Machine Learning para generar predicciones precisas con un margen de error de tan solo **±5 raciones por día**.

---

## 🏗️ Arquitectura del Proyecto (Pipeline)

El sistema se compone de **4 pilares** que se ejecutan en secuencia:

### 1. 📊 Generación de Datos — `scripts/generate_data.py`

Genera un histórico sintético de **1.280 registros** (6 meses de ventas, de lunes a viernes) para **10 restaurantes** reales de Azca. La simulación incorpora lógica de negocio real:

- **Clima**: temperatura y lluvia simulados con distribuciones estadísticas de Madrid.
- **Estacionalidad**: menús rotativos por temporada (otoño, invierno, primavera).
- **Patrones de demanda**: caída del **~27% los viernes**, efecto de la lluvia (**-11%**), factor precio y capacidad del local.
- **Festivos**: excluye los festivos oficiales de Madrid.

### 2. 🔍 Análisis Exploratorio — `scripts/eda_rapido.py`

Valida visualmente que los patrones generados son coherentes antes de entrenar el modelo:

- **Gráfico 1**: Media de menús vendidos por día de la semana (confirma la caída del viernes).
- **Gráfico 2**: Impacto de la lluvia en ventas, desglosado por tipo de cocina.
- Los gráficos se guardan como PNG en `data/`.

### 3. 🧠 Cerebro Predictivo — `scripts/train_model.py`

Pipeline completo de Machine Learning con **scikit-learn**:

| Paso | Componente | Descripción |
|------|-----------|-------------|
| Preprocesado | `ColumnTransformer` + `OneHotEncoder` | Convierte texto (día, cocina, temporada) en flags numéricas |
| Modelo | `RandomForestRegressor` | 100 árboles, max_depth=10 |
| Resultado | **MAE = 5.21 menús** | El modelo se equivoca en ~5 raciones por restaurante y día |

El pipeline completo (preprocesador + modelo) se guarda en `models/demand_predictor.pkl` para uso en producción.

### 4. 🔮 Intérprete de Menú — `scripts/interprete_menu.py`

Sistema **híbrido** de clasificación de platos — nuestra pieza estrella:

```
┌──────────────────────────────────────────────┐
│            NOMBRE DEL PLATO (OCR)            │
└──────────────────┬───────────────────────────┘
                   │
        ┌──────────▼──────────┐
        │  🛡️ Regla Especial   │ ← Platos fríos (gazpacho, salmorejo...)
        │   (100% confianza)  │
        └──────────┬──────────┘
                   │ No match
        ┌──────────▼──────────┐
        │  📖 Capa 1:          │ ← ~100 palabras clave por cocina
        │   Diccionario        │   (taco→Mexicana, risotto→Italiana...)
        │   (100% confianza)  │
        └──────────┬──────────┘
                   │ No match
        ┌──────────▼──────────┐
        │  🤖 Capa 2:          │ ← mDeBERTa multilingüe (HuggingFace)
        │   NLP Zero-Shot      │   Entiende semánticamente el plato
        │   (XX% confianza)   │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │  📊 Random Forest    │
        │   → Raciones/día    │
        └─────────────────────┘
```

---

## 📁 Estructura de Carpetas

```
theSpoon/
├── data/                          # Datos y gráficos generados
│   ├── historico_ventas.csv       # Dataset principal (1.280 registros)
│   ├── eda_menus_por_dia_semana.png
│   ├── eda_lluvia_por_cocina.png
│   └── evaluacion_modelo.png
├── models/                        # Modelos entrenados
│   └── demand_predictor.pkl       # Pipeline completo (OHE + Random Forest)
├── scripts/                       # Scripts del pipeline ML
│   ├── generate_data.py           # Paso 1: Generación de datos sintéticos
│   ├── eda_rapido.py              # Paso 2: Análisis Exploratorio
│   ├── train_model.py             # Paso 3: Entrenamiento del modelo
│   ├── interprete_menu.py         # Paso 4: Intérprete híbrido de menú
│   └── test_prediccion.py         # Test end-to-end del modelo
├── app/                           # Aplicación Streamlit (próximamente)
├── ocr/                           # Integración OCR (Azure AI Vision)
├── requirements.txt               # Dependencias del proyecto
└── README.md
```

---

## ⚡ Cómo Ejecutarlo

### 1. Clonar el repositorio

```bash
git clone git@github.com:srincondelacruz/theSpoon.git
cd theSpoon
```

### 2. Crear y activar el entorno virtual

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar el pipeline en orden

```bash
# Paso 1: Generar el dataset de ventas
python scripts/generate_data.py

# Paso 2: Análisis Exploratorio (genera PNGs en data/)
python scripts/eda_rapido.py

# Paso 3: Entrenar el modelo (genera .pkl en models/)
python scripts/train_model.py

# Paso 4: Probar el intérprete híbrido de menú
python scripts/interprete_menu.py

# (Opcional) Test rápido de predicción
python scripts/test_prediccion.py
```

---

## 🚀 Stack Tecnológico

| Componente | Tecnología |
|-----------|------------|
| Datos | Pandas, NumPy, Faker |
| ML | scikit-learn (Random Forest) |
| NLP | Hugging Face Transformers (mDeBERTa) |
| Visualización | Matplotlib, Seaborn |
| OCR | Azure AI Vision API |
| App/Demo | Streamlit |

---

## 🗺️ Roadmap — Próximos Pasos

- [ ] **App Streamlit**: interfaz visual para que los restaurantes consulten predicciones en tiempo real.
- [ ] **Integración OCR**: subir foto del menú → extraer platos automáticamente con Azure AI Vision.
- [ ] **API REST**: endpoint para que cualquier aplicación pueda consumir las predicciones.
- [ ] **Modelo XGBoost**: comparar rendimiento con el Random Forest actual.
- [ ] **Dashboard de métricas**: panel con KPIs de desperdicio y ahorro estimado.

---

## 👥 Equipo

Práctica Final IA Tradicional — Marzo 2026
