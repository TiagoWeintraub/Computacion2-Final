#!/bin/bash

# chmod +x install.sh --> Dar permisos de ejecución

# Crear entorno virtual en la carpeta app/
python3 -m venv /.

# Activar el entorno virtual de la carpeta app/
source boot.sh

# Actualizar pip
pip3 install --upgrade pip

# Instalar dependencias
pip3 install requests

echo "El entorno virtual se ha configurado y las dependencias se han instalado."

$SHELL