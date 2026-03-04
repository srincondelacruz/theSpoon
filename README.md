# 🥄 La Cuchara

**Gestión inteligente de menús para la zona de Azca, Madrid.**

La Cuchara permite a los restaurantes subir fotos de sus menús diarios, extraer automáticamente los platos mediante OCR, y ofrecer predicciones de demanda basadas en Machine Learning. Los empleados de la zona pueden buscar, filtrar y valorar menús cercanos.

## 🚀 Stack Tecnológico

- **App/Demo**: Streamlit (Python)
- **OCR**: Azure AI Vision API
- **Datos**: CSV / Pandas
- **ML**: scikit-learn, XGBoost
- **Generación de datos**: Faker, NumPy

## 📁 Estructura del Proyecto

```
theSpoon/
├── app/                     # Aplicación Streamlit
│   ├── app.py               # App principal
│   ├── pages/               # Vistas (Admin / Empleado)
│   └── utils.py             # Funciones auxiliares
├── data/                    # Datos sintéticos (CSVs)
├── models/                  # Modelos entrenados
├── ocr/                     # Integración OCR
├── sample_menus/            # Fotos de menús de ejemplo
└── scripts/                 # Scripts de generación y entrenamiento
```

## ⚡ Instalación

```bash
pip install -r requirements.txt
```

## 🏃 Uso

### Generar datos sintéticos
```bash
python scripts/generate_data.py
```

### Entrenar modelo predictivo
```bash
python scripts/train_model.py
```

### Lanzar la aplicación
```bash
streamlit run app/app.py
```

## 👥 Equipo

Práctica Final IA Tradicional — Marzo 2026
