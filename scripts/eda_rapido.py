"""
La Cuchara — EDA Rápido (Análisis Exploratorio de Datos)
========================================================
Lee data/historico_ventas.csv y genera dos gráficos PNG para validar
que los patrones de demanda son realistas antes de entrenar el modelo.

Gráficos generados:
  1. data/eda_menus_por_dia_semana.png  — Media de menús vendidos por día de la semana
  2. data/eda_lluvia_por_cocina.png     — Impacto de la lluvia en ventas por tipo de cocina
"""

import os
import sys

import matplotlib
matplotlib.use("Agg")  # Backend sin interfaz gráfica (para generar PNGs sin pantalla)

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# ============================================================
# CONFIGURACIÓN
# ============================================================
# Ruta base del proyecto (subimos un nivel desde scripts/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")                          # Carpeta de datos
CSV_PATH = os.path.join(DATA_DIR, "historico_ventas.csv")           # Archivo de entrada

# Estilo visual de los gráficos
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
plt.rcParams["figure.dpi"] = 150  # Alta resolución


def main():
    """Ejecuta el análisis exploratorio y guarda los gráficos."""

    # --------------------------------------------------------
    # 1. Cargar los datos
    # --------------------------------------------------------
    print("📂 Cargando datos desde:", CSV_PATH)
    df = pd.read_csv(CSV_PATH)
    print(f"   ✅ {len(df):,} registros cargados ({df['fecha'].nunique()} días, "
          f"{df['restaurante_id'].nunique()} restaurantes)\n")

    # Orden correcto de los días de la semana (lunes a viernes)
    orden_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]

    # ============================================================
    # GRÁFICO 1: Media de menús vendidos por día de la semana
    # ============================================================
    print("📊 Gráfico 1: Menús vendidos por día de la semana...")

    # Calculamos la media de menús vendidos agrupando por día de la semana
    media_por_dia = (
        df.groupby("dia_semana")["menus_vendidos"]
        .mean()
        .reindex(orden_dias)  # Reordenamos de lunes a viernes
    )

    # Creamos la figura
    fig1, ax1 = plt.subplots(figsize=(10, 6))

    # Usamos colores que resalten el viernes (que esperamos más bajo)
    colores = ["#4C72B0"] * 5  # Azul por defecto para todos
    colores[4] = "#DD4444"     # Rojo para el viernes (resaltamos la caída)

    # Dibujamos el gráfico de barras
    barras = ax1.bar(media_por_dia.index, media_por_dia.values, color=colores,
                     edgecolor="white", linewidth=1.2)

    # Añadimos el valor numérico encima de cada barra
    for barra in barras:
        altura = barra.get_height()
        ax1.text(barra.get_x() + barra.get_width() / 2, altura + 0.3,
                 f"{altura:.1f}", ha="center", va="bottom", fontweight="bold", fontsize=11)

    # Configuración de ejes y título
    ax1.set_title("Media de menús vendidos por día de la semana",
                  fontsize=14, fontweight="bold", pad=15)
    ax1.set_xlabel("Día de la semana", fontsize=12)
    ax1.set_ylabel("Media de menús vendidos", fontsize=12)
    ax1.set_ylim(0, media_por_dia.max() * 1.15)  # Dejamos espacio arriba para las etiquetas
    ax1.spines["top"].set_visible(False)           # Quitamos borde superior
    ax1.spines["right"].set_visible(False)         # Quitamos borde derecho

    # Añadimos una anotación explicativa
    ax1.annotate("↓ Caída esperada\n   los viernes",
                 xy=(4, media_por_dia.iloc[4]),
                 xytext=(3.2, media_por_dia.iloc[4] + 4),
                 fontsize=10, color="#DD4444", fontweight="bold",
                 arrowprops={"arrowstyle": "->", "color": "#DD4444", "linewidth": 1.5})

    plt.tight_layout()

    # Guardamos como PNG
    ruta_png1 = os.path.join(DATA_DIR, "eda_menus_por_dia_semana.png")
    fig1.savefig(ruta_png1, bbox_inches="tight")
    plt.close(fig1)
    print(f"   ✅ Guardado en: {ruta_png1}")

    # ============================================================
    # GRÁFICO 2: Impacto de la lluvia en ventas por tipo de cocina
    # ============================================================
    print("📊 Gráfico 2: Impacto de la lluvia por tipo de cocina...")

    # Preparamos los datos: convertimos lluvia a etiqueta legible
    df["lluvia_label"] = df["lluvia"].map({True: "Con lluvia", False: "Sin lluvia"})

    # Calculamos la media de menús vendidos por tipo de cocina y condición de lluvia
    media_lluvia = (
        df.groupby(["tipo_cocina", "lluvia_label"])["menus_vendidos"]
        .mean()
        .reset_index()
    )

    # Ordenamos los tipos de cocina por demanda media total (de mayor a menor)
    orden_cocina = (
        df.groupby("tipo_cocina")["menus_vendidos"]
        .mean()
        .sort_values(ascending=False)
        .index.tolist()
    )

    # Creamos la figura
    fig2, ax2 = plt.subplots(figsize=(12, 7))

    # Dibujamos barras agrupadas (una por condición de lluvia, por tipo de cocina)
    sns.barplot(
        data=media_lluvia,
        x="tipo_cocina",
        y="menus_vendidos",
        hue="lluvia_label",
        order=orden_cocina,
        palette={"Sin lluvia": "#F4A460", "Con lluvia": "#4682B4"},
        edgecolor="white",
        linewidth=1.2,
        ax=ax2,
    )

    # Configuración de ejes y título
    ax2.set_title("Impacto de la lluvia en menús vendidos por tipo de cocina",
                  fontsize=14, fontweight="bold", pad=15)
    ax2.set_xlabel("Tipo de cocina", fontsize=12)
    ax2.set_ylabel("Media de menús vendidos", fontsize=12)
    ax2.legend(title="Condición", fontsize=11, title_fontsize=11)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    # Rotamos las etiquetas del eje X para que no se solapen
    plt.xticks(rotation=25, ha="right")

    # Añadimos líneas de referencia con el valor medio global
    media_global = df["menus_vendidos"].mean()
    ax2.axhline(y=media_global, color="gray", linestyle="--", linewidth=1, alpha=0.7)
    ax2.text(len(orden_cocina) - 1, media_global + 0.5,
             f"Media global: {media_global:.1f}",
             ha="right", fontsize=9, color="gray", fontstyle="italic")

    plt.tight_layout()

    # Guardamos como PNG
    ruta_png2 = os.path.join(DATA_DIR, "eda_lluvia_por_cocina.png")
    fig2.savefig(ruta_png2, bbox_inches="tight")
    plt.close(fig2)
    print(f"   ✅ Guardado en: {ruta_png2}")

    # ============================================================
    # Resumen final
    # ============================================================
    print("\n" + "=" * 55)
    print("📋 RESUMEN DEL EDA")
    print("=" * 55)

    # Verificamos el patrón del viernes
    media_vie = media_por_dia["Viernes"]
    media_lun_jue = media_por_dia[["Lunes", "Martes", "Miércoles", "Jueves"]].mean()
    caida_pct = (1 - media_vie / media_lun_jue) * 100
    print(f"\n📉 Caída de demanda los viernes:")
    print(f"   Media lun–jue: {media_lun_jue:.1f} menús")
    print(f"   Media viernes: {media_vie:.1f} menús")
    print(f"   Caída:         {caida_pct:.1f}%")
    print(f"   {'✅ Patrón CONFIRMADO' if caida_pct > 15 else '⚠️ Patrón débil'}")

    # Verificamos el efecto lluvia
    media_sin_lluvia = df[~df["lluvia"]]["menus_vendidos"].mean()
    media_con_lluvia = df[df["lluvia"]]["menus_vendidos"].mean()
    efecto_lluvia = (1 - media_con_lluvia / media_sin_lluvia) * 100
    print(f"\n🌧️ Efecto de la lluvia:")
    print(f"   Sin lluvia: {media_sin_lluvia:.1f} menús (media)")
    print(f"   Con lluvia: {media_con_lluvia:.1f} menús (media)")
    print(f"   Reducción:  {efecto_lluvia:.1f}%")
    print(f"   {'✅ Patrón CONFIRMADO' if efecto_lluvia > 5 else '⚠️ Patrón débil'}")

    print(f"\n📁 Gráficos guardados en: {DATA_DIR}/")
    print(f"   • eda_menus_por_dia_semana.png")
    print(f"   • eda_lluvia_por_cocina.png")
    print("\n✨ ¡EDA completado!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
