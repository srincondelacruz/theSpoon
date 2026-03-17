from datetime import datetime

def get_current_weather(lat=40.4168, lon=-3.7038):
    """
    Simula el clima basado en la temporada actual para evitar errores de red.
    """
    now = datetime.now()
    month = now.month
    
    # Simulación simple por temporada
    if month in [12, 1, 2]: # Invierno
        temp, raining = 8.5, True
    elif month in [6, 7, 8]: # Verano
        temp, raining = 28.0, False
    else: # Primavera/Otoño
        temp, raining = 18.0, False
        
    return {
        "temp": temp,
        "raining": raining,
        "code": 0
    }

def get_context_date_info():
    """
    Calcula automáticamente el día de la semana y la temporada del sistema.
    """
    now = datetime.now()
    
    # Día de la semana en español
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    dia_semana = dias[now.weekday()]
    
    # Temporada
    month = now.month
    if month in [12, 1, 2]:
        temporada = "invierno"
    elif month in [3, 4, 5]:
        temporada = "primavera"
    elif month in [6, 7, 8]:
        temporada = "verano"
    else:
        temporada = "otoño"
        
    return dia_semana, temporada
