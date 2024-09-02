# Best Search

1. Es un programa en donde los clientes pueden buscar un libro a través de su código ISBN13.
2. El servidor buscará el precio de ese libro en 3 librerías diferentes (Web Scraping), mostrando al cliente donde le conviene comprar el libro. 
3. El servidor admite múltiples clientes de forma concurrente. (Cada cliente es un hilo separado)  
4. El servidor almacena los logs en un archivo .log 


# Listar puertos en escucha con netstat
netstat -an | grep LISTEN

# Probar ipv6 e ipv4 con Telnet
telnet ::1  5555 
telnet 127.0.0.1  5555