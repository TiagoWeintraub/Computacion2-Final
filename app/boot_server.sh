# chmod +x boot.sh --> Dar permisos de ejecución

# Activar el entorno virtual de la carpeta app/
echo "Activando entorno virtual y ejecutando servidor..." 
source bin/activate
source .env
python servidor.py