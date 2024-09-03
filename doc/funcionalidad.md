## ---------------- Funcionalidad del Sistema Best Search ---------------- ##

### Cliente:
- Conexión al Servidor: El cliente se conecta al servidor utilizando sockets para enviar y recibir información en tiempo real.
- Interfaz de Usuario: Se ofrece una interfaz por línea de comandos para que los usuarios puedan interactuar con el servidor.
- Envío de Solicitudes: Los usuarios envían solicitudes al servidor para buscar libros.

### Servidor:
- Gestión de Conexiones: El servidor acepta conexiones a través de sockets (IPv4 e IPv6).
- Manejo de múltiples clientes de forma concurrente (Multi hilos): Cada cliente es un hilo diferente.
- Servidor Multiprocesos: Los sockets se ejecutan en procesos separados. 
- Manejo de Errores: Se implementan mecanismos para detectar y gestionar diferentes tipos de errores, incluyendo datos inválidos, problemas de conexión, libros no encontrados, errores de web scraping, entre otros.
# Web Scraping
- Web Scraping: Se utiliza BeautifulSoup para scrapear, utilizando ThreadPoolExecutor para buscar en diferentes sitios web de forma concurrente.
- Lógica de Selección: Se comparan los resultados para determinar la mejor opción, considerando factores como el precio y disponibilidad.
# Logs:
- Los logs del servidor se almacenan en un archivo llamado "servidor.log". Esto se realiza en un proceso separado al main, conectando el proceso principal al proceso de logs con colas (Multiprocessing Queue), permitiendo acceder a los registros del servidor.



## ------------------------------ Utilidades ------------------------------ ##

# Listar puertos en escucha con netstat
netstat -an | grep LISTEN

# Probar ipv6 e ipv4 con Telnet
telnet ::1  5555 
telnet 127.0.0.1  5555

# Docker 
docker build -t compu2-final .