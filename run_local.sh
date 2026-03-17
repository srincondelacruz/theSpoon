#!/bin/bash

# ==============================================================================
# 🚀 Lanzador The Spoon: Inicia Backend (FastAPI) y Frontend (React/Vite)
# ==============================================================================

# Colores para los logs
GREEN="\03[.0;32m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

echo -e "${GREEN}Iniciando la plataforma theSpoon en entorno local...${NC}\n"

# 1. Matar procesos huérfanos anteriores por si acaso (Limpieza en puertos 8000 y Vite)
echo "Limpiando puertos ocupados de sesiones anteriores (Opcional)..."
pkill -f "uvicorn" >/dev/null 2>&1
pkill -f "vite" >/dev/null 2>&1

# 2. Iniciar el Backend (FastAPI) en segundo plano
echo -e "\n${BLUE}[Backend]${NC} Activando entorno de Python y levantando Inteligencia Artificial (FastAPI)..."
if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
elif [ -f venv/bin/activate ]; then
    source venv/bin/activate
else
    echo -e "\033[0;31m[Error] No se encontró entorno virtual (venv/ ni .venv/). Créalo primero.\033[0m"
    exit 1
fi
uvicorn app.api:app --reload --port 8000 --host 0.0.0.0 &
FASTAPI_PID=$!

# Darle unos segundos al backend para cargar el modelo mDeBERTa "pesado" antes de mostrar info
sleep 3
echo -e "${BLUE}[Backend]${NC} 🔥 FastAPI sirviendo en: http://localhost:8000"

# 3. Iniciar el Frontend (React + Vite)
echo -e "\n${GREEN}[Frontend]${NC} Levantando servidor web local de React..."
cd web || exit
npm run dev -- --open &
VITE_PID=$!

echo -e "\n${GREEN}[Sistema]${NC} 🟢 ¡Todo funcionando maravillosamente!"
echo -e "          -> Cierra con \033[1;31mCtrl+C\033[0m para apagar los dos servidores a la vez."

# Función para detener todo limpiamente si el usuario presiona Ctrl+C en la terminal
cleanup() {
    echo -e "\n\n${GREEN}[Sistema]${NC} 🛑 Apagando los servidores... ¡Hasta la próxima!"
    kill $FASTAPI_PID
    kill $VITE_PID
    exit
}

# Atrapar la señal de cierre (Ctrl+C / SIGINT) y ejecutar la limpieza
trap cleanup SIGINT EXIT

# Esperar infinitamente a que termine alguno de los procesos (básicamente bloquea para no cerrar)
wait $FASTAPI_PID $VITE_PID
