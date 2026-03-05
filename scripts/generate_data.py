"""
La Cuchara - Generador de Datos Sintéticos
==========================================
Genera el archivo data/historico_ventas.csv con un histórico de 6 meses
de actividad (lunes a viernes) para 10 restaurantes de la zona de Azca, Madrid.

Columnas del CSV resultante:
  fecha, restaurante_id, nombre_restaurante, tipo_cocina, direccion,
  precio_menu, dia_semana, dia_semana_num, temporada, primer_plato,
  segundo_plato, postre, temperatura, lluvia, es_festivo,
  menus_vendidos, ingresos, valoracion_media
"""

# ============================================================
# IMPORTACIONES
# ============================================================
import os        # Para manejar rutas de archivos y crear directorios
import random    # Para generar números aleatorios con distribución uniforme
import sys       # Para códigos de salida del programa
from datetime import datetime, timedelta  # Para manipular fechas

import numpy as np   # Para distribuciones estadísticas (normal, etc.)
import pandas as pd  # Para crear y manipular DataFrames y exportar a CSV

# ============================================================
# SEMILLA — garantiza que los datos sean reproducibles
# ============================================================
SEED = 42                    # Semilla fija para reproducibilidad
random.seed(SEED)            # Fijamos la semilla de random
np.random.seed(SEED)         # Fijamos la semilla de numpy

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================
FECHA_INICIO = datetime(2025, 9, 1)   # Inicio del histórico: 1 de septiembre 2025
FECHA_FIN = datetime(2026, 3, 3)      # Fin del histórico: 3 de marzo 2026 (~6 meses)

# Ruta del directorio de salida: carpeta "data" en la raíz del proyecto
OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),  # Subimos un nivel desde scripts/
    "data"  # Carpeta de destino
)

# Nombre del archivo CSV de salida
OUTPUT_FILE = "historico_ventas.csv"

# ============================================================
# DATOS DE LOS 10 RESTAURANTES DE AZCA
# ============================================================
# Cada restaurante tiene nombre, dirección, tipo de cocina,
# coordenadas GPS, precio medio del menú y capacidad máxima.
RESTAURANTES = [
    {
        "restaurante_id": 1,                              # Identificador único
        "nombre": "Casa Hortensia",                        # Nombre del restaurante
        "direccion": "Calle Orense 32, Madrid",            # Dirección física
        "tipo_cocina": "Tradicional Española",             # Tipo de cocina que ofrece
        "latitud": 40.4512,                                # Coordenada GPS: latitud
        "longitud": -3.6925,                               # Coordenada GPS: longitud
        "precio_medio": 12.50,                             # Precio medio del menú del día (€)
        "capacidad_maxima": 55,                            # Número máximo de comensales
    },
    {
        "restaurante_id": 2,
        "nombre": "El Rincón de Azca",
        "direccion": "Paseo de la Castellana 89, Madrid",
        "tipo_cocina": "Mediterránea",
        "latitud": 40.4518,
        "longitud": -3.6932,
        "precio_medio": 13.00,
        "capacidad_maxima": 60,
    },
    {
        "restaurante_id": 3,
        "nombre": "La Taberna del Volapié",
        "direccion": "Calle Rosario Pino 12, Madrid",
        "tipo_cocina": "Tradicional Española",
        "latitud": 40.4505,
        "longitud": -3.6910,
        "precio_medio": 11.50,
        "capacidad_maxima": 45,
    },
    {
        "restaurante_id": 4,
        "nombre": "Trattoria Azca",
        "direccion": "Calle Capitán Haya 19, Madrid",
        "tipo_cocina": "Italiana",
        "latitud": 40.4525,
        "longitud": -3.6940,
        "precio_medio": 14.00,
        "capacidad_maxima": 50,
    },
    {
        "restaurante_id": 5,
        "nombre": "Wok Garden",
        "direccion": "Calle Orense 16, Madrid",
        "tipo_cocina": "Asiática",
        "latitud": 40.4530,
        "longitud": -3.6918,
        "precio_medio": 11.00,
        "capacidad_maxima": 65,
    },
    {
        "restaurante_id": 6,
        "nombre": "La Albufera",
        "direccion": "Calle Pedro Teixeira 8, Madrid",
        "tipo_cocina": "Arrocería",
        "latitud": 40.4508,
        "longitud": -3.6950,
        "precio_medio": 14.50,
        "capacidad_maxima": 40,
    },
    {
        "restaurante_id": 7,
        "nombre": "El Asador de Azca",
        "direccion": "Paseo de la Castellana 93, Madrid",
        "tipo_cocina": "Asador",
        "latitud": 40.4522,
        "longitud": -3.6928,
        "precio_medio": 15.00,
        "capacidad_maxima": 50,
    },
    {
        "restaurante_id": 8,
        "nombre": "Verde & Más",
        "direccion": "Calle Sor Ángela de la Cruz 4, Madrid",
        "tipo_cocina": "Vegetariana",
        "latitud": 40.4515,
        "longitud": -3.6935,
        "precio_medio": 12.00,
        "capacidad_maxima": 35,
    },
    {
        "restaurante_id": 9,
        "nombre": "Marisquería Nautilus",
        "direccion": "Calle Orense 68, Madrid",
        "tipo_cocina": "Marisquería",
        "latitud": 40.4528,
        "longitud": -3.6912,
        "precio_medio": 16.00,
        "capacidad_maxima": 45,
    },
    {
        "restaurante_id": 10,
        "nombre": "Taquería La Lupe",
        "direccion": "Calle Capitán Haya 1, Madrid",
        "tipo_cocina": "Mexicana",
        "latitud": 40.4502,
        "longitud": -3.6942,
        "precio_medio": 11.00,
        "capacidad_maxima": 55,
    },
]

# ============================================================
# CATÁLOGO DE PLATOS POR TIPO DE COCINA Y TEMPORADA
# ============================================================
# Temporadas: otoño (sep-nov), invierno (dic-feb), primavera (mar+)
# Cada cocina tiene 5 primeros, 5 segundos y 5 postres por temporada.
# Los menús rotan semanalmente: un plato distinto cada día (lun-vie).

PLATOS_PRIMEROS = {
    "Tradicional Española": {
        "otoño":     ["Sopa castellana", "Lentejas estofadas", "Crema de calabaza", "Judías con chorizo", "Puchero madrileño"],
        "invierno":  ["Cocido madrileño", "Sopa de ajo", "Lentejas con verduras", "Fabada asturiana", "Potaje de garbanzos"],
        "primavera": ["Gazpacho", "Ensalada mixta", "Crema de espárragos", "Sopa fría de tomate", "Menestra de verduras"],
    },
    "Mediterránea": {
        "otoño":     ["Ensalada templada de setas", "Crema de puerros", "Hummus con crudités", "Tabulé", "Sopa minestrone"],
        "invierno":  ["Crema de zanahoria y jengibre", "Ensalada César", "Sopa de cebolla", "Falafel con ensalada", "Crema de champiñones"],
        "primavera": ["Ensalada griega", "Gazpacho andaluz", "Tabulé de quinoa", "Carpaccio de tomate", "Crema fría de pepino"],
    },
    "Italiana": {
        "otoño":     ["Minestrone", "Bruschetta de tomate", "Ensalada caprese", "Crema de calabacín", "Antipasto variado"],
        "invierno":  ["Risotto de setas", "Sopa toscana", "Carpaccio de ternera", "Crema de parmesano", "Bruschetta de champiñones"],
        "primavera": ["Ensalada italiana", "Caprese con burrata", "Vitello tonnato", "Gazpacho italiano", "Carpaccio de calabacín"],
    },
    "Asiática": {
        "otoño":     ["Sopa de miso", "Rollitos de primavera", "Gyozas de cerdo", "Ensalada de wakame", "Edamame"],
        "invierno":  ["Ramen de cerdo", "Sopa tom yum", "Wonton soup", "Dim sum variado", "Sopa pho"],
        "primavera": ["Ensalada thai", "Rollitos vietnamitas", "Sopa fría de pepino", "Edamame con sal", "Tataki de atún"],
    },
    "Arrocería": {
        "otoño":     ["Ensalada valenciana", "Croquetas de jamón", "Mejillones al vapor", "Pimientos del piquillo rellenos", "Sopa de pescado"],
        "invierno":  ["Sopa de marisco", "Croquetas de bacalao", "Calamares a la romana", "Pimientos asados", "Patatas bravas"],
        "primavera": ["Ensalada de pulpo", "Gazpacho manchego", "Mejillones en escabeche", "Boquerones en vinagre", "Ensaladilla rusa"],
    },
    "Asador": {
        "otoño":     ["Sopa castellana de setas", "Morcilla de Burgos", "Pimientos asados", "Ensalada templada", "Patatas revolconas"],
        "invierno":  ["Sopa de cocido", "Croquetas caseras", "Morcilla con pimientos", "Ensalada de escarola", "Revuelto de morcilla"],
        "primavera": ["Ensalada de tomate", "Parrillada de verduras", "Espárragos a la brasa", "Cogollos a la plancha", "Pimientos de Padrón"],
    },
    "Vegetariana": {
        "otoño":     ["Crema de calabaza y curry", "Ensalada de quinoa", "Hummus casero", "Sopa de lentejas rojas", "Rollitos de col"],
        "invierno":  ["Crema de brócoli", "Bowl de boniato asado", "Sopa de miso vegana", "Falafel casero", "Crema de coliflor"],
        "primavera": ["Gazpacho verde", "Ensalada power bowl", "Ceviche de mango", "Crema fría de guisantes", "Buddha bowl"],
    },
    "Marisquería": {
        "otoño":     ["Salpicón de marisco", "Gambas al ajillo", "Mejillones a la marinera", "Ensalada de mariscos", "Sopa de pescado"],
        "invierno":  ["Sopa de marisco", "Cazuela de almejas", "Pulpo a la gallega", "Navajas a la plancha", "Vieiras gratinadas"],
        "primavera": ["Cóctel de gambas", "Ensalada de langostinos", "Ceviche de lubina", "Tartar de atún", "Gazpacho de marisco"],
    },
    "Mexicana": {
        "otoño":     ["Sopa azteca", "Nachos con guacamole", "Elote asado", "Quesadillas de queso", "Totopos con pico de gallo"],
        "invierno":  ["Pozole rojo", "Queso fundido con chorizo", "Sopa de tortilla", "Nachos gratinados", "Flautas de pollo"],
        "primavera": ["Guacamole fresco", "Ensalada mexicana", "Ceviche de camarón", "Esquites", "Tostadas de aguacate"],
    },
}

PLATOS_SEGUNDOS = {
    "Tradicional Española": {
        "otoño":     ["Pollo asado con patatas", "Merluza en salsa verde", "Albóndigas en salsa", "Lomo a la plancha", "Callos a la madrileña"],
        "invierno":  ["Rabo de toro", "Bacalao al pil pil", "Estofado de ternera", "Secreto ibérico", "Chuletillas de cordero"],
        "primavera": ["Pollo al limón", "Merluza a la romana", "Ternera a la plancha", "Pechuga a la plancha", "Calamares encebollados"],
    },
    "Mediterránea": {
        "otoño":     ["Dorada al horno", "Pollo al romero", "Brochetas de ternera", "Salmón con verduras", "Musaka griega"],
        "invierno":  ["Cordero al horno", "Lubina a la sal", "Moussaka", "Tajín de pollo", "Bacalao confitado"],
        "primavera": ["Atún a la plancha", "Pollo con limón y hierbas", "Brochetas de gambas", "Sardinas a la brasa", "Hamburguesa mediterránea"],
    },
    "Italiana": {
        "otoño":     ["Pasta carbonara", "Lasaña boloñesa", "Scaloppine al limón", "Pizza margarita", "Ravioli de ricotta"],
        "invierno":  ["Ossobuco alla milanese", "Pasta al ragú", "Saltimbocca romana", "Pizza quattro formaggi", "Ñoquis al pesto"],
        "primavera": ["Pasta primavera", "Pizza napolitana", "Pollo alla cacciatora", "Linguine alle vongole", "Penne arrabbiata"],
    },
    "Asiática": {
        "otoño":     ["Pollo teriyaki", "Pad thai", "Cerdo agridulce", "Curry rojo de pollo", "Arroz frito con gambas"],
        "invierno":  ["Ramen tonkotsu", "Curry japonés", "Pato pekinés", "Bibimbap", "Noodles con ternera"],
        "primavera": ["Salmón teriyaki", "Pollo kung pao", "Arroz jazmín con verduras", "Yakisoba", "Tofu mapo"],
    },
    "Arrocería": {
        "otoño":     ["Arroz con pollo", "Paella de marisco", "Arroz al horno", "Arroz negro", "Fideuá"],
        "invierno":  ["Arroz caldoso de bogavante", "Paella mixta", "Arroz con costillas", "Arroz a banda", "Arroz con verduras"],
        "primavera": ["Paella valenciana", "Arroz con gambas", "Arroz de verduras", "Fideuá de marisco", "Arroz meloso de setas"],
    },
    "Asador": {
        "otoño":     ["Chuletón de ternera", "Cochinillo asado", "Costillas de cerdo", "Entrecot a la brasa", "Chuletas de cordero"],
        "invierno":  ["Lechazo asado", "Chuletón de buey", "Secreto ibérico a la brasa", "Solomillo al whisky", "Codillo asado"],
        "primavera": ["Entrecot con patatas", "Pollo de corral asado", "Brochetas de cordero", "Costillas BBQ", "Hamburguesa gourmet"],
    },
    "Vegetariana": {
        "otoño":     ["Curry de garbanzos", "Lasaña de verduras", "Hamburguesa vegana", "Tofu salteado", "Bowl de lentejas"],
        "invierno":  ["Estofado de soja", "Risotto de setas", "Chili sin carne", "Guiso de judías", "Pasta integral con verduras"],
        "primavera": ["Bowl hawaiano vegano", "Wrap de falafel", "Pasta de calabacín", "Ensalada power", "Tacos de jackfruit"],
    },
    "Marisquería": {
        "otoño":     ["Merluza a la vasca", "Paella de marisco", "Lubina a la espalda", "Gambas a la plancha", "Rape alangostado"],
        "invierno":  ["Bacalao gratinado", "Zarzuela de pescado", "Rodaballo al horno", "Merluza en salsa", "Chipirones encebollados"],
        "primavera": ["Dorada a la sal", "Gambas al ajillo", "Atún rojo a la plancha", "Pulpo a la brasa", "Langostinos a la plancha"],
    },
    "Mexicana": {
        "otoño":     ["Tacos al pastor", "Enchiladas rojas", "Burrito de pollo", "Fajitas de ternera", "Chili con carne"],
        "invierno":  ["Tamales de cerdo", "Mole poblano", "Burritos de carne asada", "Enchiladas verdes", "Chilaquiles rojos"],
        "primavera": ["Tacos de pescado", "Bowl mexicano", "Quesadillas de pollo", "Fajitas de gambas", "Burrito bowl vegetal"],
    },
}

# Los postres son compartidos por todos los restaurantes, varían por temporada
POSTRES = {
    "otoño":     ["Arroz con leche", "Flan casero", "Tarta de manzana", "Natillas", "Coulant de chocolate"],
    "invierno":  ["Torrijas", "Tarta de queso", "Crema catalana", "Brownie con helado", "Leche frita"],
    "primavera": ["Fresones con nata", "Helado artesano", "Sorbete de limón", "Tarta de frutas", "Panna cotta"],
}

# ============================================================
# DATOS CLIMÁTICOS DE MADRID (por mes)
# ============================================================
# Temperatura media, desviación estándar y probabilidad de lluvia
CLIMA_MADRID = {
    9:  {"temp_media": 24, "temp_std": 4, "prob_lluvia": 0.15},  # Septiembre: caluroso, poca lluvia
    10: {"temp_media": 18, "temp_std": 4, "prob_lluvia": 0.25},  # Octubre: templado, algo de lluvia
    11: {"temp_media": 12, "temp_std": 3, "prob_lluvia": 0.25},  # Noviembre: fresco, algo de lluvia
    12: {"temp_media": 7,  "temp_std": 3, "prob_lluvia": 0.20},  # Diciembre: frío
    1:  {"temp_media": 6,  "temp_std": 3, "prob_lluvia": 0.20},  # Enero: el mes más frío
    2:  {"temp_media": 8,  "temp_std": 3, "prob_lluvia": 0.20},  # Febrero: frío, empieza a subir
    3:  {"temp_media": 12, "temp_std": 4, "prob_lluvia": 0.20},  # Marzo: primavera incipiente
}

# ============================================================
# FESTIVOS EN MADRID (dentro del rango de fechas)
# ============================================================
# Estos días los restaurantes cierran o tienen muy baja actividad
FESTIVOS = [
    datetime(2025, 10, 12),   # Fiesta Nacional de España
    datetime(2025, 11, 1),    # Día de Todos los Santos
    datetime(2025, 11, 9),    # Virgen de la Almudena (patrona de Madrid)
    datetime(2025, 12, 6),    # Día de la Constitución
    datetime(2025, 12, 8),    # Inmaculada Concepción
    datetime(2025, 12, 25),   # Navidad
    datetime(2026, 1, 1),     # Año Nuevo
    datetime(2026, 1, 6),     # Día de Reyes
]

# ============================================================
# Nombres de los días de la semana en español
# ============================================================
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def get_temporada(fecha: datetime) -> str:
    """Devuelve la temporada gastronómica según el mes de la fecha."""
    mes = fecha.month  # Extraemos el número de mes (1-12)
    if mes in (9, 10, 11):       # Septiembre, octubre, noviembre
        return "otoño"
    elif mes in (12, 1, 2):      # Diciembre, enero, febrero
        return "invierno"
    else:                        # Marzo en adelante
        return "primavera"


def generar_clima(fecha: datetime) -> tuple:
    """
    Simula la temperatura y la lluvia para un día concreto en Madrid.
    Devuelve una tupla (temperatura_en_grados, llueve_bool).
    """
    mes = fecha.month                                     # Mes de la fecha
    clima = CLIMA_MADRID[mes]                             # Obtenemos los parámetros climáticos del mes
    # Generamos la temperatura con distribución normal (media ± desviación)
    temperatura = round(np.random.normal(clima["temp_media"], clima["temp_std"]), 1)
    temperatura = max(-2, min(40, temperatura))           # Limitamos a un rango realista (-2°C a 40°C)
    # La lluvia es un evento binario con la probabilidad del mes
    lluvia = bool(np.random.random() < clima["prob_lluvia"])
    return temperatura, lluvia                            # Devolvemos ambos valores


def es_festivo(fecha: datetime) -> bool:
    """Comprueba si una fecha concreta es un día festivo."""
    return fecha in FESTIVOS  # True si la fecha está en la lista de festivos


def es_laborable(fecha: datetime) -> bool:
    """
    Comprueba si una fecha es día laborable:
    - Debe ser de lunes (0) a viernes (4)
    - No debe ser festivo
    """
    return fecha.weekday() < 5 and not es_festivo(fecha)


def obtener_menu_del_dia(tipo_cocina: str, temporada: str, dia_semana_num: int) -> tuple:
    """
    Devuelve el menú (primer plato, segundo plato, postre) para un restaurante
    en función de su tipo de cocina, la temporada y el día de la semana (0-4).
    Los platos rotan semanalmente: día 0 → plato[0], día 1 → plato[1], etc.
    """
    # Obtenemos la lista de primeros platos para esta cocina y temporada
    primeros = PLATOS_PRIMEROS.get(tipo_cocina, {}).get(temporada, [])
    # Obtenemos la lista de segundos platos
    segundos = PLATOS_SEGUNDOS.get(tipo_cocina, {}).get(temporada, [])
    # Obtenemos la lista de postres (iguales para todos los restaurantes)
    postres = POSTRES.get(temporada, [])

    # Seleccionamos el plato correspondiente al día de la semana (rotación cíclica)
    primer = primeros[dia_semana_num % len(primeros)] if primeros else "Ensalada mixta"
    segundo = segundos[dia_semana_num % len(segundos)] if segundos else "Pollo a la plancha"
    postre = postres[dia_semana_num % len(postres)] if postres else "Fruta del tiempo"

    return primer, segundo, postre  # Devolvemos los tres platos del menú


def calcular_demanda(capacidad: int, dia_semana_num: int, temperatura: float,
                     lluvia: bool, precio_medio: float) -> int:
    """
    Calcula el número de menús vendidos en un día concreto.

    La demanda depende de varios factores realistas:
    1. Capacidad del restaurante (base)
    2. Día de la semana (viernes → menos demanda de menú del día)
    3. Clima: lluvia reduce ligeramente la afluencia general
    4. Temperatura: frío → más gente come en restaurante
    5. Precio: restaurantes más baratos atraen más clientes
    """
    # Demanda base: entre el 60% y el 95% de la capacidad máxima
    demanda_base = capacidad * np.random.uniform(0.60, 0.95)

    # Factor por día de la semana (los viernes la gente prefiere carta o irse de la zona)
    factores_dia = {
        0: 1.00,   # Lunes: demanda normal
        1: 1.05,   # Martes: ligeramente por encima (día punta)
        2: 1.02,   # Miércoles: ligeramente por encima
        3: 0.98,   # Jueves: ligeramente por debajo
        4: 0.75,   # Viernes: mucha gente no come menú del día
    }
    factor_dia = factores_dia[dia_semana_num]  # Seleccionamos el factor del día

    # Factor clima: si llueve, baja un 10% la afluencia
    factor_clima = 0.90 if lluvia else 1.0

    # Factor temperatura: frío extremo → más gente busca restaurantes cálidos
    if temperatura < 10:
        factor_temp = 1.10    # +10% cuando hace mucho frío
    elif temperatura > 25:
        factor_temp = 0.92    # -8% cuando hace mucho calor (la gente come ligero)
    else:
        factor_temp = 1.0     # Temperatura agradable, factor neutro

    # Factor precio: los restaurantes más baratos venden más menús
    # 13€ es el precio medio de referencia en la zona
    factor_precio = 1.0 + (13 - precio_medio) * 0.02

    # Ruido aleatorio: variación diaria impredecible (±8%)
    ruido = np.random.normal(1.0, 0.08)

    # Cálculo final: multiplicamos todos los factores
    menus_vendidos = int(demanda_base * factor_dia * factor_clima * factor_temp * factor_precio * ruido)
    menus_vendidos = max(5, menus_vendidos)  # Mínimo 5 menús (nunca vendemos 0)

    return menus_vendidos


def generar_valoracion_media(tipo_cocina: str, precio_medio: float) -> float:
    """
    Genera una valoración media simulada para un día concreto.
    Las valoraciones van de 1.0 a 5.0 estrellas.

    Factores:
    - Cada tipo de cocina tiene una calidad base aleatoria
    - Restaurantes más caros tienden a tener mejor valoración
    - Se añade ruido diario (unos días salen mejor, otros peor)
    """
    # Calidad base: entre 3.0 y 4.5 (la mayoría de restaurantes son decentes)
    calidad_base = np.random.uniform(3.0, 4.5)

    # Bonus por precio (asumimos que pagar más = mejor calidad, con matices)
    bonus_precio = (precio_medio - 11.0) * 0.08  # Pequeño ajuste por precio

    # Ruido diario: variación natural del servicio
    ruido = np.random.normal(0, 0.3)

    # Sumamos todo y limitamos entre 1.0 y 5.0
    valoracion = round(calidad_base + bonus_precio + ruido, 1)
    valoracion = max(1.0, min(5.0, valoracion))  # Clamp entre 1 y 5

    return valoracion


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def main():
    """
    Genera el archivo historico_ventas.csv con todos los datos de ventas
    de los 10 restaurantes de Azca durante 6 meses (lunes a viernes).
    """
    print("🥄 La Cuchara — Generador de Histórico de Ventas")
    print("=" * 60)
    print(f"  Periodo:       {FECHA_INICIO.strftime('%d/%m/%Y')} → {FECHA_FIN.strftime('%d/%m/%Y')}")
    print(f"  Restaurantes:  {len(RESTAURANTES)}")
    print(f"  Días hábiles:  lunes a viernes (excluyendo festivos)")
    print("=" * 60 + "\n")

    # Crear el directorio de salida si no existe
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Lista donde acumularemos todas las filas del CSV
    registros = []

    # --------------------------------------------------------
    # Iteramos día a día desde FECHA_INICIO hasta FECHA_FIN
    # --------------------------------------------------------
    fecha_actual = FECHA_INICIO  # Comenzamos por el primer día

    while fecha_actual <= FECHA_FIN:
        # Solo procesamos días laborables (lunes a viernes, sin festivos)
        if es_laborable(fecha_actual):

            # Determinamos la temporada gastronómica de esta fecha
            temporada = get_temporada(fecha_actual)

            # Número del día de la semana (0=Lunes, 4=Viernes)
            dia_semana_num = fecha_actual.weekday()

            # Nombre del día en español
            dia_semana = DIAS_SEMANA[dia_semana_num]

            # Simulamos el clima de este día
            temperatura, lluvia = generar_clima(fecha_actual)

            # ------------------------------------------------
            # Para cada restaurante, generamos su registro de ventas
            # ------------------------------------------------
            for rest in RESTAURANTES:
                # Obtenemos el menú del día según cocina, temporada y día
                primer, segundo, postre = obtener_menu_del_dia(
                    rest["tipo_cocina"],  # Tipo de cocina del restaurante
                    temporada,            # Temporada actual
                    dia_semana_num        # Día de la semana (0-4)
                )

                # Calculamos cuántos menús se vendieron este día
                menus_vendidos = calcular_demanda(
                    rest["capacidad_maxima"],  # Capacidad del restaurante
                    dia_semana_num,            # Día de la semana
                    temperatura,               # Temperatura del día
                    lluvia,                    # Si lluvió o no
                    rest["precio_medio"]       # Precio del menú
                )

                # Calculamos los ingresos: menús vendidos × precio del menú
                ingresos = round(menus_vendidos * rest["precio_medio"], 2)

                # Generamos una valoración media simulada para este día
                valoracion_media = generar_valoracion_media(
                    rest["tipo_cocina"],   # Tipo de cocina
                    rest["precio_medio"]   # Precio medio
                )

                # Añadimos el registro completo a la lista
                registros.append({
                    "fecha":             fecha_actual.strftime("%Y-%m-%d"),  # Fecha en formato ISO
                    "restaurante_id":    rest["restaurante_id"],             # ID del restaurante
                    "nombre_restaurante": rest["nombre"],                    # Nombre del restaurante
                    "tipo_cocina":       rest["tipo_cocina"],                # Tipo de cocina
                    "direccion":         rest["direccion"],                  # Dirección física
                    "precio_menu":       rest["precio_medio"],              # Precio del menú (€)
                    "dia_semana":        dia_semana,                        # Nombre del día (Lunes, etc.)
                    "dia_semana_num":    dia_semana_num,                    # Número del día (0-4)
                    "temporada":         temporada,                         # Temporada (otoño/invierno/primavera)
                    "primer_plato":      primer,                            # Primer plato del menú
                    "segundo_plato":     segundo,                           # Segundo plato del menú
                    "postre":            postre,                            # Postre del menú
                    "temperatura":       temperatura,                       # Temperatura (°C) del día
                    "lluvia":            lluvia,                            # True/False si llovió
                    "es_festivo":        False,                             # Siempre False (filtramos festivos)
                    "menus_vendidos":    menus_vendidos,                    # Número de menús vendidos
                    "ingresos":          ingresos,                         # Ingresos totales del día (€)
                    "valoracion_media":  valoracion_media,                 # Valoración media (1-5 estrellas)
                })

        # Avanzamos al día siguiente
        fecha_actual += timedelta(days=1)

    # --------------------------------------------------------
    # Convertimos la lista de registros a DataFrame de pandas
    # --------------------------------------------------------
    df = pd.DataFrame(registros)

    # --------------------------------------------------------
    # Guardamos el DataFrame como CSV con codificación UTF-8
    # --------------------------------------------------------
    ruta_csv = os.path.join(OUTPUT_DIR, OUTPUT_FILE)  # Ruta completa del archivo
    df.to_csv(ruta_csv, index=False, encoding="utf-8")  # Guardamos sin índice numérico

    # --------------------------------------------------------
    # Imprimimos un resumen de los datos generados
    # --------------------------------------------------------
    print("✅ Archivo generado con éxito!")
    print(f"   📁 Ruta: {ruta_csv}")
    print(f"   📊 Total de registros: {len(df):,}")
    print(f"   📅 Días únicos: {df['fecha'].nunique()}")
    print(f"   🏪 Restaurantes: {df['restaurante_id'].nunique()}")
    print()

    # Resumen por temporada
    print("📊 Resumen por temporada:")
    print("-" * 50)
    resumen_temp = df.groupby("temporada").agg(
        registros=("fecha", "count"),                         # Total de registros por temporada
        menus_totales=("menus_vendidos", "sum"),               # Total de menús vendidos
        ingreso_total=("ingresos", "sum"),                    # Ingresos totales
        valoracion_media=("valoracion_media", "mean"),        # Valoración media
        temp_media=("temperatura", "mean"),                   # Temperatura media
    ).round(2)
    print(resumen_temp.to_string())
    print()

    # Resumen por restaurante
    print("🏪 Resumen por restaurante:")
    print("-" * 60)
    resumen_rest = df.groupby("nombre_restaurante").agg(
        menus_totales=("menus_vendidos", "sum"),              # Total de menús vendidos
        ingreso_total=("ingresos", "sum"),                   # Ingresos totales
        valoracion_media=("valoracion_media", "mean"),       # Valoración media
    ).sort_values("ingreso_total", ascending=False).round(2)  # Ordenamos por ingresos (mayor primero)
    print(resumen_rest.to_string())
    print()

    # Estadísticas generales
    print("📈 Estadísticas generales:")
    print(f"   🍽️  Total menús vendidos:  {df['menus_vendidos'].sum():,}")
    print(f"   💰 Ingresos totales:       {df['ingresos'].sum():,.2f} €")
    print(f"   ⭐ Valoración media:       {df['valoracion_media'].mean():.2f}")
    print(f"   🌡️  Temperatura media:     {df['temperatura'].mean():.1f}°C")
    print(f"   🌧️  Días con lluvia:       {df[df['lluvia']]['fecha'].nunique()} de {df['fecha'].nunique()}")

    print("\n✨ ¡Generación completada con éxito!")
    return 0  # Código de salida: 0 = sin errores


# ============================================================
# PUNTO DE ENTRADA: ejecuta main() cuando se lanza el script
# ============================================================
if __name__ == "__main__":
    sys.exit(main())  # Ejecutamos main() y devolvemos su código de salida
