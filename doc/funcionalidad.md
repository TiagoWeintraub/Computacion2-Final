# Funcionalidad del Sistema Best Search:

### Cliente:
- Conexión al Servidor: El cliente se conecta al servidor utilizando sockets para enviar y recibir información en tiempo real.
- Interfaz de Usuario: Se ofrece una interfaz por línea de comandos para que los usuarios puedan interactuar con el servidor.
- Envío de Solicitudes: Los usuarios envían solicitudes al servidor para buscar libros.

### Servidor:
- Gestión de Conexiones: El servidor acepta conexiones a través de sockets.
- Manejo de múltiples clientes de forma concurrente: Cada cliente es un proceso diferente. 
- Manejo de Errores: Se implementan mecanismos para detectar y gestionar diferentes tipos de errores, incluyendo datos inválidos, problemas de conexión, libros no encontrados, errores en el proceso de web scraping, entre otros.
# Web Scraping
- Web Scraping: Se utiliza BeautifulSoup para scrapear, utilizando ThreadPoolExecutor para buscar en diferentes sitios web de forma concurrente.
- Lógica de Selección: Se comparan los resultados para determinar la mejor opción, considerando factores como el precio y disponibilidad.
# Logs:
- Los logs del servidor se almacenan en un archivo log. Esto se realiza en un proceso separado al main, conectando ambos procesos con Queue, permitiendo acceder a los registros del servidor.
