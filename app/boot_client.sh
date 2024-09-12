# chmod +x boot_client.sh --> Dar permisos de ejecución

# Activar el entorno virtual de la carpeta app/
echo "Activando entorno virtual y ejecutando cliente..." 
source bin/activate
source .env
python cliente.py