"""
La Cuchara — Entrenamiento del Modelo Predictivo (Pasos 1–4)
===============================================================
Paso 1: Carga de datos y división Train / Test.
Paso 2: Preprocesamiento (One-Hot Encoding de columnas categóricas).
Paso 3: Entrenamiento del modelo (Pipeline: preprocesador + Random Forest).
Paso 4: Evaluación visual (MAE, gráfico scatter) y guardado del modelo.
"""

import os                                          # Para manejar rutas de archivos
import pandas as pd                                # Para cargar y manipular el CSV
import joblib                                      # Para guardar/cargar el modelo entrenado

import matplotlib                                  # Para configurar el backend gráfico
matplotlib.use("Agg")                              # Backend sin interfaz (genera PNGs sin pantalla)
import matplotlib.pyplot as plt                    # Para crear gráficos
import seaborn as sns                              # Para gráficos estadísticos bonitos

from sklearn.model_selection import train_test_split    # Para dividir en Train / Test
from sklearn.compose import ColumnTransformer            # Para aplicar transformaciones por columna
from sklearn.preprocessing import OneHotEncoder          # Para convertir texto en flags (0/1)
from sklearn.ensemble import RandomForestRegressor       # El modelo: Random Forest para regresión
from sklearn.pipeline import Pipeline                    # Para encadenar preprocesado + modelo
from sklearn.metrics import mean_absolute_error          # Métrica de error: MAE


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "historico_ventas.csv")

print("📂 Cargando datos desde:", CSV_PATH)
df = pd.read_csv(CSV_PATH)                         # Leemos el CSV completo en un DataFrame
print(f"   ✅ {len(df):,} registros cargados\n")

# ============================================================
# 2. CREAR LA MATRIZ X (features / variables predictoras)
# ============================================================
# Seleccionamos solo las columnas que el modelo usará para aprender:
#   - dia_semana:   día de la semana (Lunes, Martes, ...) → categórica
#   - tipo_cocina:  tipo de restaurante (Italiana, Asiática, ...) → categórica
#   - lluvia:       si llovió ese día (True/False) → booleana
#   - temperatura:  grados centígrados → numérica
#   - precio_menu:  precio del menú del día en euros → numérica
#   - temporada:    otoño, invierno o primavera → categórica
columnas_features = ["dia_semana", "tipo_cocina", "lluvia", "temperatura", "precio_menu", "temporada"]
X = df[columnas_features]                          # Extraemos solo esas columnas

print("📋 Features (X):")
print(f"   Forma: {X.shape[0]} filas × {X.shape[1]} columnas")
print(f"   Columnas: {list(X.columns)}\n")

# ============================================================
# 3. CREAR EL VECTOR y (target / lo que queremos predecir)
# ============================================================
# El objetivo del modelo es predecir cuántos menús se venderán cada día
y = df["menus_vendidos"]                           # Serie con los valores a predecir

print("🎯 Target (y): menus_vendidos")
print(f"   Media: {y.mean():.1f} | Mín: {y.min()} | Máx: {y.max()}\n")

# ============================================================
# 4. DIVIDIR EN TRAIN (80%) Y TEST (20%)
# ============================================================
# train_test_split baraja los datos y los reparte en dos cajas:
#   - Train (80%): el modelo APRENDE con estos datos
#   - Test  (20%): el modelo se EVALÚA con estos datos (nunca los ha visto)
#
# random_state=42 fija la semilla del generador aleatorio.
# Así, cada vez que ejecutemos el script, la división será EXACTAMENTE la misma.
# Esto es crucial para reproducibilidad: si tú y yo ejecutamos el mismo código,
# obtendremos los mismos conjuntos de Train y Test.
X_train, X_test, y_train, y_test = train_test_split(
    X, y,                                          # Datos de entrada y salida
    test_size=0.20,                                # 20% para Test
    random_state=42,                               # Semilla fija → resultado reproducible
)

print("📊 DIVISIÓN TRAIN / TEST")
print("=" * 50)
print(f"   🟢 Train: {len(X_train):,} filas ({len(X_train)/len(X)*100:.0f}%)")
print(f"   🔵 Test:  {len(X_test):,} filas ({len(X_test)/len(X)*100:.0f}%)")
print(f"   📦 Total: {len(X):,} filas")
print()


print("🔍 Verificación de distribución (media de menus_vendidos):")
print(f"   Train: {y_train.mean():.1f} menús/día")
print(f"   Test:  {y_test.mean():.1f} menús/día")
print(f"   {'✅ Distribución equilibrada' if abs(y_train.mean() - y_test.mean()) < 3 else '⚠️ Posible desbalanceo'}")

# ============================================================
# 5. PREPROCESAMIENTO: Convertir texto en flags numéricas
# ============================================================
# El modelo Random Forest solo entiende NÚMEROS. Las columnas como
# "dia_semana" (Lunes, Martes...) o "tipo_cocina" (Italiana, Asiática...)
# son TEXTO. Necesitamos convertirlas en columnas binarias (0/1).
#
# Ejemplo: la columna "dia_semana" con valor "Lunes" se convierte en:
#   dia_semana_Lunes=1, dia_semana_Martes=0, dia_semana_Miércoles=0, ...
#
# Esto se llama ONE-HOT ENCODING (codificación "uno caliente").

# Lista de columnas categóricas (las que contienen texto)
categoricas = ["dia_semana", "tipo_cocina", "temporada"]

# Las columnas numéricas (temperatura, precio_menu) y booleanas (lluvia)
# ya son números, así que las dejamos pasar tal cual con remainder='passthrough'.
preprocesador = ColumnTransformer(
    transformers=[
        # ("nombre", transformador, columnas_a_transformar)
        ("cat", OneHotEncoder(handle_unknown="ignore"), categoricas),
        # handle_unknown='ignore' → si en el futuro aparece una categoría
        # que el modelo nunca vio (ej: "Coreana"), no dará error:
        # simplemente pondrá TODAS las flags de esa columna a 0.
    ],
    remainder="passthrough",  # Las columnas no listadas (lluvia, temperatura, precio_menu)
                              # pasan al resultado sin modificar.
)

# --- PASO CRÍTICO: fit_transform vs transform ---
#
# ¿Por qué usamos fit_transform en Train pero solo transform en Test?
#
# fit_transform(X_train) hace DOS cosas:
#   1. FIT   → Aprende el vocabulario (qué valores existen: Lunes, Martes...)
#   2. TRANSFORM → Aplica la conversión a flags
#
# transform(X_test) hace solo UNA cosa:
#   1. TRANSFORM → Aplica la conversión usando el vocabulario que ya aprendió
#
# Si hiciéramos fit_transform también en Test, le estaríamos "chivando" al
# modelo información del examen final. El modelo solo debe aprender el
# vocabulario de los datos de entrenamiento, NUNCA del test.
# Esto se llama evitar "DATA LEAKAGE" (fuga de datos).

print("\n" + "=" * 50)
print("🔧 PREPROCESAMIENTO (One-Hot Encoding)")
print("=" * 50)

# Mostramos la forma ANTES de procesar
print(f"\n   ANTES  → X_train: {X_train.shape[0]} filas × {X_train.shape[1]} columnas")
print(f"             X_test:  {X_test.shape[0]} filas × {X_test.shape[1]} columnas")

# Aplicamos el preprocesador
X_train_procesado = preprocesador.fit_transform(X_train)  # Aprende vocabulario + transforma
X_test_procesado = preprocesador.transform(X_test)        # Solo transforma (NO aprende)

# Mostramos la forma DESPUÉS de procesar
print(f"\n   DESPUÉS → X_train_procesado: {X_train_procesado.shape[0]} filas × {X_train_procesado.shape[1]} columnas")
print(f"             X_test_procesado:  {X_test_procesado.shape[0]} filas × {X_test_procesado.shape[1]} columnas")

# Calculamos cuántas flags nuevas se han creado
flags_nuevas = X_train_procesado.shape[1] - X_train.shape[1]
print(f"\n   📊 Columnas originales:  {X_train.shape[1]}")
print(f"   🏷️  Columnas tras OHE:   {X_train_procesado.shape[1]}")
print(f"   ✨ Flags nuevas creadas: {flags_nuevas}")

# Mostramos los nombres de todas las flags generadas
nombres_flags = preprocesador.get_feature_names_out()  # Nombres de todas las columnas resultantes
print(f"\n   🏷️  Nombres de las columnas resultantes:")
for i, nombre in enumerate(nombres_flags):
    print(f"      [{i+1:2d}] {nombre}")

# ============================================================
# 6. PIPELINE: Empaquetamos preprocesador + modelo en una sola pieza
# ============================================================
# ¿Por qué un Pipeline y no hacer los pasos sueltos?
#
# Un Pipeline es como una cadena de montaje: encadena automáticamente
# el preprocesador (One-Hot Encoding) con el modelo (Random Forest).
#
# Ventajas:
#   1. IMPOSIBLE olvidarse de preprocesar. Si alguien usa el modelo
#      guardado en producción, el Pipeline aplica la transformación
#      automáticamente antes de predecir.
#   2. Evita DATA LEAKAGE. fit() entrena todo el pipeline de golpe,
#      garantizando que el preprocesador solo aprende de Train.
#   3. Código más limpio. Una sola llamada a .fit() y .predict()
#      en lugar de múltiples pasos manuales.
#   4. Guardado fácil. Con joblib guardamos UN solo archivo .pkl
#      que contiene preprocesador + modelo juntos.

print("\n" + "=" * 50)
print("🌳 PASO 3: ENTRENAMIENTO (Pipeline + Random Forest)")
print("=" * 50)

# Creamos el pipeline con dos pasos:
#   1. "preprocesador" → convierte texto en flags (ColumnTransformer)
#   2. "modelo" → Random Forest con 100 árboles de decisión
pipeline = Pipeline([
    ("preprocesador", preprocesador),            # Paso 1: One-Hot Encoding
    ("modelo", RandomForestRegressor(
        n_estimators=100,     # 100 árboles de decisión votan juntos
        max_depth=10,         # Máxima profundidad de cada árbol (evita sobreajuste)
        random_state=42,      # Semilla para reproducibilidad
    )),
])

# Entrenamos el pipeline completo con los datos de Train
# (el pipeline internamente primero transforma X_train y luego entrena el Random Forest)
print("\n🧠 Entrenando la IA... esto puede tardar unos segundos")
pipeline.fit(X_train, y_train)                   # ¡A aprender!
print("   ✅ Modelo entrenado con éxito\n")

# ============================================================
# 7. PREDICCIÓN Y EVALUACIÓN (MAE)
# ============================================================
# Usamos el pipeline entrenado para predecir sobre los datos de Test
# (datos que el modelo NUNCA ha visto durante el entrenamiento)
y_pred = pipeline.predict(X_test)                # Predicciones sobre el examen final

# Calculamos el MAE (Mean Absolute Error / Error Absoluto Medio)
# El MAE nos dice: "de media, ¿cuántas raciones se equivoca el modelo?"
mae = mean_absolute_error(y_test, y_pred)         # Diferencia media entre real y predicho

# Mostramos el resultado de forma destacada
print("=" * 50)
print("🎯 PASO 4: EVALUACIÓN DEL MODELO")
print("=" * 50)
print()
print("   ┌──────────────────────────────────────┐")
print(f"   │  📊 MAE = {mae:.2f} menús de error medio   │")
print("   └──────────────────────────────────────┘")
print()
print(f"   💡 ¿Qué significa esto para La Cuchara?")
print(f"   → El modelo se equivoca en ~{mae:.0f} raciones por restaurante y día.")
print(f"   → Si un restaurante vende 40 menús, el modelo predice entre")
print(f"     {40 - mae:.0f} y {40 + mae:.0f} menús (margen de ±{mae:.0f}).")
print(f"   → Esto permite planificar con bastante precisión cuánta")
print(f"     comida preparar cada día, reduciendo el desperdicio.")

# ============================================================
# 8. GRÁFICO: Scatter Plot — Raciones Reales vs Predichas
# ============================================================
print("\n📊 Generando gráfico de evaluación...")

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
plt.rcParams["figure.dpi"] = 150                  # Alta resolución

fig, ax = plt.subplots(figsize=(8, 8))            # Figura cuadrada

# Dibujamos cada punto: X = valor real, Y = valor predicho
# Si el modelo fuera perfecto, todos los puntos estarían SOBRE la diagonal.
ax.scatter(y_test, y_pred, alpha=0.5, s=40, color="#4C72B0",
           edgecolor="white", linewidth=0.5, label="Predicciones")

# Dibujamos la línea diagonal roja = "predicción perfecta"
# (donde real == predicho)
limite_min = min(y_test.min(), y_pred.min()) - 2  # Margen inferior
limite_max = max(y_test.max(), y_pred.max()) + 2  # Margen superior
ax.plot([limite_min, limite_max], [limite_min, limite_max],
        color="#DD4444", linewidth=2, linestyle="--",
        label="Predicción perfecta")

# Configuración de ejes y título
ax.set_xlim(limite_min, limite_max)
ax.set_ylim(limite_min, limite_max)
ax.set_xlabel("Menús vendidos (REAL)", fontsize=13)
ax.set_ylabel("Menús vendidos (PREDICCIÓN)", fontsize=13)
ax.set_title("Evaluación del Modelo: Real vs Predicho",
             fontsize=14, fontweight="bold", pad=15)
ax.legend(fontsize=11)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Añadimos una anotación con el MAE dentro del gráfico
ax.text(0.05, 0.92, f"MAE = {mae:.2f} menús",
        transform=ax.transAxes, fontsize=13, fontweight="bold",
        color="#333333",
        bbox={"boxstyle": "round,pad=0.4", "facecolor": "#FFFACD",
              "edgecolor": "#DAA520", "alpha": 0.9})

plt.tight_layout()

# Guardamos el gráfico
ruta_png = os.path.join(BASE_DIR, "data", "evaluacion_modelo.png")
fig.savefig(ruta_png, bbox_inches="tight")
plt.close(fig)
print(f"   ✅ Guardado en: {ruta_png}")

# ============================================================
# 9. GUARDAR EL MODELO ENTRENADO
# ============================================================
# Guardamos el pipeline completo (preprocesador + modelo) como un archivo .pkl
# Cualquiera puede cargarlo después con joblib.load() y hacer predicciones
# SIN necesidad de volver a entrenar ni preprocesar manualmente.
ruta_modelo = os.path.join(BASE_DIR, "models", "demand_predictor.pkl")
os.makedirs(os.path.dirname(ruta_modelo), exist_ok=True)  # Crear carpeta models/ si no existe
joblib.dump(pipeline, ruta_modelo)                # Guardamos el pipeline completo

print(f"\n💾 Modelo guardado en: {ruta_modelo}")
print("   (Incluye preprocesador + Random Forest en un solo archivo)")
print("\n✨ ¡Entrenamiento y evaluación completados con éxito!")
