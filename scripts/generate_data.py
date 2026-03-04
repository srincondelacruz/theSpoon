"""
La Cuchara - Generador de Datos Sintéticos
==========================================
Genera un histórico de 6+ meses de datos para ~10 restaurantes en Azca (Madrid).

Datasets generados:
- restaurantes.csv: Información de los restaurantes
- platos.csv: Catálogo de platos disponibles
- menus.csv: Menús diarios (primer plato, segundo, postre)
- valoraciones.csv: Valoraciones de usuarios
- demanda.csv: Demanda diaria con factores climáticos
"""

import os
import random
import sys
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

# ============================================================
# SEED para reproducibilidad
# ============================================================
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# ============================================================
# CONFIGURACIÓN
# ============================================================
NUM_RESTAURANTES = 10
NUM_USUARIOS = 500  # Empleados que valoran platos
FECHA_INICIO = datetime(2025, 9, 1)  # 1 de septiembre 2025
FECHA_FIN = datetime(2026, 3, 3)     # ~6 meses de datos
TOTAL_EMPLEADOS_AZCA = 27000
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

# ============================================================
# DATOS BASE: Restaurantes reales de la zona de Azca
# ============================================================
RESTAURANTES_INFO = [
    {
        "nombre": "Casa Hortensia",
        "direccion": "Calle Orense 32, Madrid",
        "tipo_cocina": "Tradicional Española",
        "latitud": 40.4512,
        "longitud": -3.6925,
        "precio_medio": 12.50,
    },
    {
        "nombre": "El Rincón de Azca",
        "direccion": "Paseo de la Castellana 89, Madrid",
        "tipo_cocina": "Mediterránea",
        "latitud": 40.4518,
        "longitud": -3.6932,
        "precio_medio": 13.00,
    },
    {
        "nombre": "La Taberna del Volapié",
        "direccion": "Calle Rosario Pino 12, Madrid",
        "tipo_cocina": "Tradicional Española",
        "latitud": 40.4505,
        "longitud": -3.6910,
        "precio_medio": 11.50,
    },
    {
        "nombre": "Trattoria Azca",
        "direccion": "Calle Capitán Haya 19, Madrid",
        "tipo_cocina": "Italiana",
        "latitud": 40.4525,
        "longitud": -3.6940,
        "precio_medio": 14.00,
    },
    {
        "nombre": "Wok Garden",
        "direccion": "Calle Orense 16, Madrid",
        "tipo_cocina": "Asiática",
        "latitud": 40.4530,
        "longitud": -3.6918,
        "precio_medio": 11.00,
    },
    {
        "nombre": "La Albufera",
        "direccion": "Calle Pedro Teixeira 8, Madrid",
        "tipo_cocina": "Arrocería",
        "latitud": 40.4508,
        "longitud": -3.6950,
        "precio_medio": 14.50,
    },
    {
        "nombre": "El Asador de Azca",
        "direccion": "Paseo de la Castellana 93, Madrid",
        "tipo_cocina": "Asador",
        "latitud": 40.4522,
        "longitud": -3.6928,
        "precio_medio": 15.00,
    },
    {
        "nombre": "Verde & Más",
        "direccion": "Calle Sor Ángela de la Cruz 4, Madrid",
        "tipo_cocina": "Vegetariana",
        "latitud": 40.4515,
        "longitud": -3.6935,
        "precio_medio": 12.00,
    },
    {
        "nombre": "Marisquería Nautilus",
        "direccion": "Calle Orense 68, Madrid",
        "tipo_cocina": "Marisquería",
        "latitud": 40.4528,
        "longitud": -3.6912,
        "precio_medio": 16.00,
    },
    {
        "nombre": "Taquería La Lupe",
        "direccion": "Calle Capitán Haya 1, Madrid",
        "tipo_cocina": "Mexicana",
        "latitud": 40.4502,
        "longitud": -3.6942,
        "precio_medio": 11.00,
    },
]

# ============================================================
# CATÁLOGO DE PLATOS por tipo de cocina y temporada
# ============================================================
# Temporadas: otoño (sep-nov), invierno (dic-feb), primavera (mar-may)
PLATOS_PRIMEROS = {
    "Tradicional Española": {
        "otoño": ["Sopa castellana", "Lentejas estofadas", "Crema de calabaza", "Judías con chorizo", "Puchero madrileño"],
        "invierno": ["Cocido madrileño", "Sopa de ajo", "Lentejas con verduras", "Fabada asturiana", "Potaje de garbanzos"],
        "primavera": ["Gazpacho", "Ensalada mixta", "Crema de espárragos", "Sopa fría de tomate", "Menestra de verduras"],
    },
    "Mediterránea": {
        "otoño": ["Ensalada templada de setas", "Crema de puerros", "Hummus con crudités", "Tabulé", "Sopa minestrone"],
        "invierno": ["Crema de zanahoria y jengibre", "Ensalada César", "Sopa de cebolla", "Falafel con ensalada", "Crema de champiñones"],
        "primavera": ["Ensalada griega", "Gazpacho andaluz", "Tabulé de quinoa", "Carpaccio de tomate", "Crema fría de pepino"],
    },
    "Italiana": {
        "otoño": ["Minestrone", "Bruschetta de tomate", "Ensalada caprese", "Crema de calabacín", "Antipasto variado"],
        "invierno": ["Risotto de setas", "Sopa toscana", "Carpaccio de ternera", "Crema de parmesano", "Bruschetta de champiñones"],
        "primavera": ["Ensalada italiana", "Caprese con burrata", "Vitello tonnato", "Gazpacho italiano", "Carpaccio de calabacín"],
    },
    "Asiática": {
        "otoño": ["Sopa de miso", "Rollitos de primavera", "Gyozas de cerdo", "Ensalada de wakame", "Edamame"],
        "invierno": ["Ramen de cerdo", "Sopa tom yum", "Wonton soup", "Dim sum variado", "Sopa pho"],
        "primavera": ["Ensalada thai", "Rollitos vietnamitas", "Sopa fría de pepino", "Edamame con sal", "Tataki de atún"],
    },
    "Arrocería": {
        "otoño": ["Ensalada valenciana", "Croquetas de jamón", "Mejillones al vapor", "Pimientos del piquillo rellenos", "Sopa de pescado"],
        "invierno": ["Sopa de marisco", "Croquetas de bacalao", "Calamares a la romana", "Pimientos asados", "Patatas bravas"],
        "primavera": ["Ensalada de pulpo", "Gazpacho manchego", "Mejillones en escabeche", "Boquerones en vinagre", "Ensaladilla rusa"],
    },
    "Asador": {
        "otoño": ["Sopa castellana de setas", "Morcilla de Burgos", "Pimientos asados", "Ensalada templada", "Patatas revolconas"],
        "invierno": ["Sopa de cocido", "Croquetas caseras", "Morcilla con pimientos", "Ensalada de escarola", "Revuelto de morcilla"],
        "primavera": ["Ensalada de tomate", "Parrillada de verduras", "Espárragos a la brasa", "Cogollos a la plancha", "Pimientos de Padrón"],
    },
    "Vegetariana": {
        "otoño": ["Crema de calabaza y curry", "Ensalada de quinoa", "Hummus casero", "Sopa de lentejas rojas", "Rollitos de col"],
        "invierno": ["Crema de brócoli", "Bowl de boniato asado", "Sopa de miso vegana", "Falafel casero", "Crema de coliflor"],
        "primavera": ["Gazpacho verde", "Ensalada power bowl", "Ceviche de mango", "Crema fría de guisantes", "Buddha bowl"],
    },
    "Marisquería": {
        "otoño": ["Salpicón de marisco", "Gambas al ajillo", "Mejillones a la marinera", "Ensalada de mariscos", "Sopa de pescado"],
        "invierno": ["Sopa de marisco", "Cazuela de almejas", "Pulpo a la gallega", "Navajas a la plancha", "Vieiras gratinadas"],
        "primavera": ["Cóctel de gambas", "Ensalada de langostinos", "Ceviche de lubina", "Tartar de atún", "Gazpacho de marisco"],
    },
    "Mexicana": {
        "otoño": ["Sopa azteca", "Nachos con guacamole", "Elote asado", "Quesadillas de queso", "Totopos con pico de gallo"],
        "invierno": ["Pozole rojo", "Queso fundido con chorizo", "Sopa de tortilla", "Nachos gratinados", "Flautas de pollo"],
        "primavera": ["Guacamole fresco", "Ensalada mexicana", "Ceviche de camarón", "Esquites", "Tostadas de aguacate"],
    },
}

PLATOS_SEGUNDOS = {
    "Tradicional Española": {
        "otoño": ["Pollo asado con patatas", "Merluza en salsa verde", "Albóndigas en salsa", "Lomo a la plancha", "Callos a la madrileña"],
        "invierno": ["Rabo de toro", "Bacalao al pil pil", "Estofado de ternera", "Secreto ibérico", "Chuletillas de cordero"],
        "primavera": ["Pollo al limón", "Merluza a la romana", "Ternera a la plancha", "Pechuga a la plancha", "Calamares encebollados"],
    },
    "Mediterránea": {
        "otoño": ["Dorada al horno", "Pollo al romero", "Brochetas de ternera", "Salmón con verduras", "Musaka griega"],
        "invierno": ["Cordero al horno", "Lubina a la sal", "Moussaka", "Tajín de pollo", "Bacalao confitado"],
        "primavera": ["Atún a la plancha", "Pollo con limón y hierbas", "Brochetas de gambas", "Sardinas a la brasa", "Hamburguesa mediterránea"],
    },
    "Italiana": {
        "otoño": ["Pasta carbonara", "Lasaña boloñesa", "Scaloppine al limón", "Pizza margarita", "Ravioli de ricotta"],
        "invierno": ["Ossobuco alla milanese", "Pasta al ragú", "Saltimbocca romana", "Pizza quattro formaggi", "Ñoquis al pesto"],
        "primavera": ["Pasta primavera", "Pizza napolitana", "Pollo alla cacciatora", "Linguine alle vongole", "Penne arrabbiata"],
    },
    "Asiática": {
        "otoño": ["Pollo teriyaki", "Pad thai", "Cerdo agridulce", "Curry rojo de pollo", "Arroz frito con gambas"],
        "invierno": ["Ramen tonkotsu", "Curry japonés", "Pato pekinés", "Bibimbap", "Noodles con ternera"],
        "primavera": ["Salmón teriyaki", "Pollo kung pao", "Arroz jazmín con verduras", "Yakisoba", "Tofu mapo"],
    },
    "Arrocería": {
        "otoño": ["Arroz con pollo", "Paella de marisco", "Arroz al horno", "Arroz negro", "Fideuá"],
        "invierno": ["Arroz caldoso de bogavante", "Paella mixta", "Arroz con costillas", "Arroz a banda", "Arroz con verduras"],
        "primavera": ["Paella valenciana", "Arroz con gambas", "Arroz de verduras", "Fideuá de marisco", "Arroz meloso de setas"],
    },
    "Asador": {
        "otoño": ["Chuletón de ternera", "Cochinillo asado", "Costillas de cerdo", "Entrecot a la brasa", "Chuletas de cordero"],
        "invierno": ["Lechazo asado", "Chuletón de buey", "Secreto ibérico a la brasa", "Solomillo al whisky", "Codillo asado"],
        "primavera": ["Entrecot con patatas", "Pollo de corral asado", "Brochetas de cordero", "Costillas BBQ", "Hamburguesa gourmet"],
    },
    "Vegetariana": {
        "otoño": ["Curry de garbanzos", "Lasaña de verduras", "Hamburguesa vegana", "Tofu salteado", "Bowl de lentejas"],
        "invierno": ["Estofado de soja", "Risotto de setas", "Chili sin carne", "Guiso de judías", "Pasta integral con verduras"],
        "primavera": ["Bowl hawaiano vegano", "Wrap de falafel", "Pasta de calabacín", "Ensalada power", "Tacos de jackfruit"],
    },
    "Marisquería": {
        "otoño": ["Merluza a la vasca", "Paella de marisco", "Lubina a la espalda", "Gambas a la plancha", "Rape alangostado"],
        "invierno": ["Bacalao gratinado", "Zarzuela de pescado", "Rodaballo al horno", "Merluza en salsa", "Chipirones encebollados"],
        "primavera": ["Dorada a la sal", "Gambas al ajillo", "Atún rojo a la plancha", "Pulpo a la brasa", "Langostinos a la plancha"],
    },
    "Mexicana": {
        "otoño": ["Tacos al pastor", "Enchiladas rojas", "Burrito de pollo", "Fajitas de ternera", "Chili con carne"],
        "invierno": ["Tamales de cerdo", "Mole poblano", "Burritos de carne asada", "Enchiladas verdes", "Chilaquiles rojos"],
        "primavera": ["Tacos de pescado", "Bowl mexicano", "Quesadillas de pollo", "Fajitas de gambas", "Burrito bowl vegetal"],
    },
}

POSTRES = {
    "otoño": ["Arroz con leche", "Flan casero", "Tarta de manzana", "Natillas", "Coulant de chocolate"],
    "invierno": ["Torrijas", "Tarta de queso", "Crema catalana", "Brownie con helado", "Leche frita"],
    "primavera": ["Fresones con nata", "Helado artesano", "Sorbete de limón", "Tarta de frutas", "Panna cotta"],
}

# ============================================================
# CLIMA SIMULADO para Madrid
# ============================================================
# Temperaturas medias y probabilidad de lluvia por mes
CLIMA_MADRID = {
    9:  {"temp_media": 24, "temp_std": 4, "prob_lluvia": 0.15},  # Septiembre
    10: {"temp_media": 18, "temp_std": 4, "prob_lluvia": 0.25},  # Octubre
    11: {"temp_media": 12, "temp_std": 3, "prob_lluvia": 0.25},  # Noviembre
    12: {"temp_media": 7,  "temp_std": 3, "prob_lluvia": 0.20},  # Diciembre
    1:  {"temp_media": 6,  "temp_std": 3, "prob_lluvia": 0.20},  # Enero
    2:  {"temp_media": 8,  "temp_std": 3, "prob_lluvia": 0.20},  # Febrero
    3:  {"temp_media": 12, "temp_std": 4, "prob_lluvia": 0.20},  # Marzo
}

# Festivos laborales en Madrid (que caen en laborable en nuestro rango)
FESTIVOS = [
    datetime(2025, 10, 12),  # Fiesta Nacional
    datetime(2025, 11, 1),   # Todos los Santos
    datetime(2025, 11, 9),   # Almudena
    datetime(2025, 12, 6),   # Constitución (sábado en 2025, pero lo dejamos)
    datetime(2025, 12, 8),   # Inmaculada
    datetime(2025, 12, 25),  # Navidad
    datetime(2026, 1, 1),    # Año Nuevo
    datetime(2026, 1, 6),    # Reyes
]


def get_temporada(fecha: datetime) -> str:
    """Devuelve la temporada según la fecha."""
    mes = fecha.month
    if mes in (9, 10, 11):
        return "otoño"
    elif mes in (12, 1, 2):
        return "invierno"
    else:
        return "primavera"


def generar_clima(fecha: datetime) -> tuple:
    """Genera temperatura y lluvia para una fecha."""
    mes = fecha.month
    clima = CLIMA_MADRID[mes]
    temperatura = round(np.random.normal(clima["temp_media"], clima["temp_std"]), 1)
    temperatura = max(-2, min(40, temperatura))
    lluvia = np.random.random() < clima["prob_lluvia"]
    return temperatura, lluvia


def es_festivo(fecha: datetime) -> bool:
    """Comprueba si una fecha es festivo."""
    return fecha in FESTIVOS


def es_laborable(fecha: datetime) -> bool:
    """Comprueba si una fecha es día laborable (lunes a viernes, no festivo)."""
    return fecha.weekday() < 5 and not es_festivo(fecha)


def generar_restaurantes() -> pd.DataFrame:
    """Genera el dataset de restaurantes."""
    print("📍 Generando restaurantes...")
    restaurantes = []
    for i, info in enumerate(RESTAURANTES_INFO):
        restaurantes.append({
            "restaurante_id": i + 1,
            "nombre": info["nombre"],
            "direccion": info["direccion"],
            "tipo_cocina": info["tipo_cocina"],
            "latitud": info["latitud"],
            "longitud": info["longitud"],
            "precio_medio": info["precio_medio"],
            "horario_apertura": "13:00",
            "horario_cierre": "16:00",
            "capacidad_maxima": random.randint(30, 80),
        })
    df = pd.DataFrame(restaurantes)
    print(f"   ✅ {len(df)} restaurantes generados")
    return df


def generar_platos(df_restaurantes: pd.DataFrame) -> pd.DataFrame:
    """Genera el catálogo completo de platos únicos."""
    print("🍽️  Generando catálogo de platos...")
    platos = []
    plato_id = 1
    seen = set()

    for _, rest in df_restaurantes.iterrows():
        tipo = rest["tipo_cocina"]
        for temporada in ["otoño", "invierno", "primavera"]:
            # Primeros platos
            for nombre in PLATOS_PRIMEROS.get(tipo, {}).get(temporada, []):
                key = (nombre, "primero")
                if key not in seen:
                    seen.add(key)
                    # Determinar tipo de plato
                    nombre_lower = nombre.lower()
                    if any(w in nombre_lower for w in ["sopa", "crema", "cocido", "lentejas", "fabada", "potaje", "ramen", "puchero", "estofado", "pozole", "guiso"]):
                        tipo_plato = "cuchara"
                    elif any(w in nombre_lower for w in ["ensalada", "gazpacho", "carpaccio", "ceviche", "buddha", "bowl"]):
                        tipo_plato = "frio"
                    elif any(w in nombre_lower for w in ["vegano", "vegana", "tofu", "quinoa", "hummus", "falafel", "edamame"]):
                        tipo_plato = "vegano"
                    else:
                        tipo_plato = "otro"
                    platos.append({
                        "plato_id": plato_id,
                        "nombre": nombre,
                        "categoria": "primero",
                        "tipo_plato": tipo_plato,
                        "temporada": temporada,
                    })
                    plato_id += 1

            # Segundos platos
            for nombre in PLATOS_SEGUNDOS.get(tipo, {}).get(temporada, []):
                key = (nombre, "segundo")
                if key not in seen:
                    seen.add(key)
                    nombre_lower = nombre.lower()
                    if any(w in nombre_lower for w in ["merluza", "bacalao", "dorada", "lubina", "salmón", "atún", "gambas", "rape", "langostinos", "sardinas", "rodaballo", "pulpo", "chipirones", "paella de marisco", "zarzuela"]):
                        tipo_plato = "pescado"
                    elif any(w in nombre_lower for w in ["pollo", "ternera", "cerdo", "cordero", "chuletón", "cochinillo", "solomillo", "secreto", "lomo", "rabo", "costillas", "entrecot", "lechazo", "codillo", "pato"]):
                        tipo_plato = "carne"
                    elif any(w in nombre_lower for w in ["vegano", "vegana", "tofu", "soja", "jackfruit"]):
                        tipo_plato = "vegano"
                    elif any(w in nombre_lower for w in ["arroz", "paella", "fideuá", "risotto"]):
                        tipo_plato = "arroz"
                    elif any(w in nombre_lower for w in ["pasta", "lasaña", "ñoquis", "ravioli", "linguine", "penne", "noodles"]):
                        tipo_plato = "pasta"
                    else:
                        tipo_plato = "otro"
                    platos.append({
                        "plato_id": plato_id,
                        "nombre": nombre,
                        "categoria": "segundo",
                        "tipo_plato": tipo_plato,
                        "temporada": temporada,
                    })
                    plato_id += 1

            # Postres
            for nombre in POSTRES.get(temporada, []):
                key = (nombre, "postre")
                if key not in seen:
                    seen.add(key)
                    platos.append({
                        "plato_id": plato_id,
                        "nombre": nombre,
                        "categoria": "postre",
                        "tipo_plato": "postre",
                        "temporada": temporada,
                    })
                    plato_id += 1

    df = pd.DataFrame(platos)
    print(f"   ✅ {len(df)} platos únicos generados")
    return df


def generar_menus(df_restaurantes: pd.DataFrame, df_platos: pd.DataFrame) -> pd.DataFrame:
    """
    Genera menús diarios para cada restaurante.
    Los menús se repiten semanalmente pero cambian por temporada.
    """
    print("📋 Generando menús diarios...")
    menus = []
    menu_id = 1

    for _, rest in df_restaurantes.iterrows():
        tipo = rest["tipo_cocina"]
        # Para cada temporada, asignamos un menú semanal (uno por día, lunes a viernes)
        menus_semanales = {}
        for temporada in ["otoño", "invierno", "primavera"]:
            primeros = PLATOS_PRIMEROS.get(tipo, {}).get(temporada, [])
            segundos = PLATOS_SEGUNDOS.get(tipo, {}).get(temporada, [])
            postres_temp = POSTRES.get(temporada, [])

            semanal = []
            for dia in range(5):  # Lunes a viernes
                primer = primeros[dia % len(primeros)] if primeros else "Ensalada mixta"
                segundo = segundos[dia % len(segundos)] if segundos else "Pollo a la plancha"
                postre = postres_temp[dia % len(postres_temp)] if postres_temp else "Fruta del tiempo"
                semanal.append((primer, segundo, postre))
            menus_semanales[temporada] = semanal

        # Generar día a día
        fecha = FECHA_INICIO
        while fecha <= FECHA_FIN:
            if es_laborable(fecha):
                temporada = get_temporada(fecha)
                dia_semana = fecha.weekday()  # 0=Lunes ... 4=Viernes
                menu_semanal = menus_semanales[temporada]
                primer, segundo, postre = menu_semanal[dia_semana]

                # Buscar plato_ids
                primer_id = df_platos[
                    (df_platos["nombre"] == primer) & (df_platos["categoria"] == "primero")
                ]["plato_id"].values
                segundo_id = df_platos[
                    (df_platos["nombre"] == segundo) & (df_platos["categoria"] == "segundo")
                ]["plato_id"].values
                postre_id = df_platos[
                    (df_platos["nombre"] == postre) & (df_platos["categoria"] == "postre")
                ]["plato_id"].values

                menus.append({
                    "menu_id": menu_id,
                    "restaurante_id": rest["restaurante_id"],
                    "fecha": fecha.strftime("%Y-%m-%d"),
                    "dia_semana": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"][dia_semana],
                    "dia_semana_num": dia_semana,
                    "temporada": temporada,
                    "primer_plato": primer,
                    "primer_plato_id": int(primer_id[0]) if len(primer_id) > 0 else None,
                    "segundo_plato": segundo,
                    "segundo_plato_id": int(segundo_id[0]) if len(segundo_id) > 0 else None,
                    "postre": postre,
                    "postre_id": int(postre_id[0]) if len(postre_id) > 0 else None,
                    "bebida_incluida": True,
                    "precio": rest["precio_medio"],
                })
                menu_id += 1
            fecha += timedelta(days=1)

    df = pd.DataFrame(menus)
    print(f"   ✅ {len(df)} menús diarios generados")
    return df


def generar_demanda(df_menus: pd.DataFrame, df_restaurantes: pd.DataFrame) -> pd.DataFrame:
    """
    Genera datos de demanda diaria por restaurante.
    
    Factores que afectan la demanda:
    - Día de la semana (viernes menos demanda de menú)
    - Clima (lluvia y frío → más platos de cuchara)
    - Capacidad del restaurante
    - Ranking/popularidad
    """
    print("📊 Generando datos de demanda...")
    demanda = []

    # Agrupar menús por fecha y restaurante
    fechas_restaurantes = df_menus.groupby(["fecha", "restaurante_id"]).first().reset_index()

    for _, row in fechas_restaurantes.iterrows():
        fecha = datetime.strptime(row["fecha"], "%Y-%m-%d")
        rest_id = row["restaurante_id"]
        rest_info = df_restaurantes[df_restaurantes["restaurante_id"] == rest_id].iloc[0]

        temperatura, lluvia = generar_clima(fecha)
        dia_semana = fecha.weekday()

        # Demanda base proporcional a la capacidad
        capacidad = rest_info["capacidad_maxima"]
        demanda_base = capacidad * np.random.uniform(0.6, 0.95)

        # Factor día de la semana (viernes menos menú del día)
        factores_dia = {0: 1.0, 1: 1.05, 2: 1.02, 3: 0.98, 4: 0.75}
        factor_dia = factores_dia[dia_semana]

        # Factor clima: lluvia reduce la demanda general en un ~10%,
        # pero aumenta la de platos de cuchara
        factor_clima = 0.90 if lluvia else 1.0

        # Factor temperatura: frío atrae más gente a restaurantes
        if temperatura < 10:
            factor_temp = 1.10
        elif temperatura > 25:
            factor_temp = 0.92
        else:
            factor_temp = 1.0

        # Factor precio (más barato → más demanda)
        precio = rest_info["precio_medio"]
        factor_precio = 1.0 + (13 - precio) * 0.02  # ~13€ es el medio

        # Ruido aleatorio
        ruido = np.random.normal(1.0, 0.08)

        platos_servidos = int(
            demanda_base * factor_dia * factor_clima * factor_temp * factor_precio * ruido
        )
        platos_servidos = max(5, platos_servidos)

        # Proporción de platos de cuchara vs total
        es_cuchara = any(
            w in row.get("primer_plato", "").lower()
            for w in ["sopa", "crema", "cocido", "lentejas", "fabada", "potaje", "ramen", "pozole"]
        )
        pct_primer_plato = 0.5  # 50% piden primer plato
        if es_cuchara and (lluvia or temperatura < 12):
            pct_primer_plato = 0.70  # Más gente pide cuchara cuando hace frío/llueve
        elif es_cuchara:
            pct_primer_plato = 0.45

        demanda.append({
            "fecha": row["fecha"],
            "restaurante_id": rest_id,
            "menu_id": row["menu_id"],
            "platos_servidos": platos_servidos,
            "raciones_primer_plato": int(platos_servidos * pct_primer_plato),
            "raciones_segundo_plato": platos_servidos,  # Todos piden segundo
            "raciones_postre": int(platos_servidos * np.random.uniform(0.55, 0.80)),
            "temperatura": temperatura,
            "lluvia": lluvia,
            "dia_semana": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"][dia_semana],
            "dia_semana_num": dia_semana,
            "es_festivo": es_festivo(fecha),
            "temporada": row["temporada"],
        })

    df = pd.DataFrame(demanda)
    print(f"   ✅ {len(df)} registros de demanda generados")
    return df


def generar_valoraciones(
    df_menus: pd.DataFrame,
    df_restaurantes: pd.DataFrame,
    num_usuarios: int = NUM_USUARIOS,
) -> pd.DataFrame:
    """
    Genera valoraciones de usuarios por plato y restaurante.
    
    Cada usuario valora aleatoriamente algunos platos que ha comido.
    Las valoraciones son más altas para restaurantes con mejor cocina
    y platos más populares.
    """
    print("⭐ Generando valoraciones de usuarios...")
    valoraciones = []
    val_id = 1

    # Cada restaurante tiene una "calidad base" aleatoria
    calidad_restaurante = {}
    for _, rest in df_restaurantes.iterrows():
        calidad_restaurante[rest["restaurante_id"]] = np.random.uniform(3.0, 4.5)

    # Seleccionar menús aleatorios para valorar
    menus_sample = df_menus.sample(frac=0.3, random_state=SEED)

    for _, menu in menus_sample.iterrows():
        # 1 a 5 usuarios valoran este menú
        n_valoraciones = np.random.randint(1, 6)
        usuarios = random.sample(range(1, num_usuarios + 1), min(n_valoraciones, num_usuarios))

        calidad = calidad_restaurante[menu["restaurante_id"]]

        for user_id in usuarios:
            # Valorar cada plato del menú
            for plato_nombre, plato_id_col, categoria in [
                (menu["primer_plato"], menu["primer_plato_id"], "primero"),
                (menu["segundo_plato"], menu["segundo_plato_id"], "segundo"),
                (menu["postre"], menu["postre_id"], "postre"),
            ]:
                if np.random.random() < 0.6:  # 60% probabilidad de valorar cada plato
                    # Puntuación basada en calidad del restaurante + ruido
                    puntuacion = calidad + np.random.normal(0, 0.7)
                    puntuacion = round(max(1, min(5, puntuacion)), 1)

                    # Generar comentario ocasional
                    comentario = ""
                    if np.random.random() < 0.15:
                        comentarios_positivos = [
                            "Muy bueno", "Excelente", "Repetiría sin duda",
                            "El mejor de la zona", "Muy rico", "Buenísimo",
                            "Como casero", "Espectacular",
                        ]
                        comentarios_negativos = [
                            "Regular", "Podría mejorar", "Algo soso",
                            "No me convenció", "Esperaba más", "Mejorable",
                        ]
                        if puntuacion >= 4:
                            comentario = random.choice(comentarios_positivos)
                        elif puntuacion <= 2.5:
                            comentario = random.choice(comentarios_negativos)

                    valoraciones.append({
                        "valoracion_id": val_id,
                        "usuario_id": user_id,
                        "restaurante_id": menu["restaurante_id"],
                        "menu_id": menu["menu_id"],
                        "plato_id": plato_id_col,
                        "plato_nombre": plato_nombre,
                        "categoria": categoria,
                        "puntuacion": puntuacion,
                        "fecha": menu["fecha"],
                        "comentario": comentario,
                    })
                    val_id += 1

    df = pd.DataFrame(valoraciones)
    print(f"   ✅ {len(df)} valoraciones generadas")
    return df


def imprimir_resumen(
    df_rest: pd.DataFrame,
    df_platos: pd.DataFrame,
    df_menus: pd.DataFrame,
    df_demanda: pd.DataFrame,
    df_valoraciones: pd.DataFrame,
):
    """Imprime un resumen de los datos generados."""
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE DATOS GENERADOS")
    print("=" * 60)
    print(f"\n{'Dataset':<25} {'Registros':>10} {'Columnas':>10}")
    print("-" * 45)
    for nombre, df in [
        ("restaurantes.csv", df_rest),
        ("platos.csv", df_platos),
        ("menus.csv", df_menus),
        ("demanda.csv", df_demanda),
        ("valoraciones.csv", df_valoraciones),
    ]:
        print(f"{nombre:<25} {len(df):>10,} {len(df.columns):>10}")

    print(f"\n📅 Rango de fechas: {FECHA_INICIO.strftime('%Y-%m-%d')} → {FECHA_FIN.strftime('%Y-%m-%d')}")
    print(f"🏪 Restaurantes: {len(df_rest)}")
    print(f"🍽️  Platos únicos: {len(df_platos)}")
    print(f"📋 Días con menú: {df_menus['fecha'].nunique()}")
    print(f"👥 Usuarios que valoran: {df_valoraciones['usuario_id'].nunique()}")
    print(f"⭐ Valoración media global: {df_valoraciones['puntuacion'].mean():.2f}")

    print(f"\n🌡️  Temperatura media: {df_demanda['temperatura'].mean():.1f}°C")
    print(f"🌧️  Días con lluvia: {df_demanda['lluvia'].sum()} ({df_demanda['lluvia'].mean()*100:.1f}%)")
    print(f"🍲 Platos servidos/día (media): {df_demanda.groupby('fecha')['platos_servidos'].sum().mean():.0f}")


def main():
    """Función principal: genera todos los datasets y los guarda en CSVs."""
    print("🥄 La Cuchara - Generador de Datos Sintéticos")
    print("=" * 60)
    print(f"Periodo: {FECHA_INICIO.strftime('%d/%m/%Y')} - {FECHA_FIN.strftime('%d/%m/%Y')}")
    print(f"Restaurantes: {NUM_RESTAURANTES}")
    print(f"Usuarios: {NUM_USUARIOS}")
    print("=" * 60 + "\n")

    # Crear directorio de salida
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Restaurantes
    df_restaurantes = generar_restaurantes()

    # 2. Catálogo de platos
    df_platos = generar_platos(df_restaurantes)

    # 3. Menús diarios
    df_menus = generar_menus(df_restaurantes, df_platos)

    # 4. Demanda
    df_demanda = generar_demanda(df_menus, df_restaurantes)

    # 5. Valoraciones
    df_valoraciones = generar_valoraciones(df_menus, df_restaurantes)

    # Guardar CSVs
    print("\n💾 Guardando archivos CSV...")
    df_restaurantes.to_csv(os.path.join(OUTPUT_DIR, "restaurantes.csv"), index=False, encoding="utf-8")
    df_platos.to_csv(os.path.join(OUTPUT_DIR, "platos.csv"), index=False, encoding="utf-8")
    df_menus.to_csv(os.path.join(OUTPUT_DIR, "menus.csv"), index=False, encoding="utf-8")
    df_demanda.to_csv(os.path.join(OUTPUT_DIR, "demanda.csv"), index=False, encoding="utf-8")
    df_valoraciones.to_csv(os.path.join(OUTPUT_DIR, "valoraciones.csv"), index=False, encoding="utf-8")
    print(f"   ✅ Archivos guardados en: {OUTPUT_DIR}")

    # Resumen
    imprimir_resumen(df_restaurantes, df_platos, df_menus, df_demanda, df_valoraciones)

    print("\n✨ ¡Generación completada con éxito!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
