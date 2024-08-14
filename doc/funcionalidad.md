# Funcionalidad del Sistema Better Search:


# Cliente:
- Conexión al Servidor: El cliente se conecta al servidor utilizando sockets para enviar y recibir información en tiempo real.
- Interfaz de Usuario: Se ofrece una interfaz de línea de comandos para que los usuarios puedan interactuar con el sistema. La interfaz permite a los usuarios buscar libros y obtener el mejor precio disponible.
- Envío de Solicitudes: Los usuarios envían solicitudes al servidor para realizar acciones específicas, como búsquedas de libros.

# Servidor:
- Gestión de Conexiones: El servidor acepta conexiones a través de sockets
- Manejo de múltiples clientes de forma concurrente: Cada cliente es un proceso diferente, asilando cada cliente y la memoria.
- Manejo de Peticiones del cliente: Cada petición del Cliente se agregará a una cola. 
- Web Scraping: Se utiliza BeautifulSoup con concurrencia para buscar resultados en diferentes sitios web, buscando el mejor precio para los libros solicitados.
- Lógica de Selección: El servidor utiliza una lógica específica para determinar el mejor resultado, considerando factores como el precio, disponibilidad y otros criterios.
- Manejo de Errores: Se implementan mecanismos para detectar y gestionar diferentes tipos de errores, incluyendo datos inválidos, problemas de conexión, libros no encontrados, errores en el proceso de web scraping, entre otros.

# Logs:
- Un proceso separado 
