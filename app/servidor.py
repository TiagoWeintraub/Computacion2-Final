from multiprocessing import Process, Queue
import socket
from concurrent.futures import ThreadPoolExecutor
import requests
from logs import Logs  
from libreria import Libreria as Lib
import select
import threading
import os

session = requests.Session()

class Scraping:
    def __init__(self, isbn):
        self.isbn = isbn

    def cuspide_page_response(self):
        try:
            response = session.get(Lib(self.isbn).cuspide_url)
            if response.status_code == 200:
                print("Scrapeando Cuspide")
                informacion_cuspide = Lib(self.isbn).scrap_cuspide(session)
                return informacion_cuspide
        except Exception as e:
            print(f"Error al scrapear Cuspide: {e}")
            return {'isbn': self.isbn, 'libro': None, 'autor': None ,'precio': None, 'libreria': 'Cúspide'}

    def casassa_page_response(self):
        try:
            response = session.get(Lib(self.isbn).casassa_url)
            if response.status_code == 200:
                print("Scrapeando Casassa")
                informacion_casassa = Lib(self.isbn).scrap_casassa(session)
                return informacion_casassa
        except Exception as e:
            print(f"Error al scrapear Casassa: {e}")
            return {'isbn': self.isbn, 'libro': None, 'autor': None ,'precio': None, 'libreria': 'Casassa y Lorenzo'}

    def sbs_page_response(self):
        try:
            response = session.get(Lib(self.isbn).sbs_url)
            if response.status_code == 200:
                print("Scrapeando SBS")
                informacion_sbs = Lib(self.isbn).scrap_sbs(session)
                return informacion_sbs
        except Exception as e:
            print(f"Error al scrapear SBS: {e}")
            return {'isbn': self.isbn, 'libro': None, 'autor': None ,'precio': None, 'libreria': 'Sbs'}

    def concurrent_scraping(self):
        try:
            with ThreadPoolExecutor(max_workers=3) as executor:
                future1 = executor.submit(self.cuspide_page_response)
                future2 = executor.submit(self.casassa_page_response)
                future3 = executor.submit(self.sbs_page_response)

                resultados = [
                    future1.result(),
                    future2.result(),
                    future3.result()
                ]
                return resultados
        except Exception as e:
            print(f"Error en concurrent_scraping: {e}")
            return None


class Servidor:
    def __init__(self, host=None, port=5555, log_queue=None):
        self.host = host
        self.port = port
        self.contador_clientes = 0
        self.log_queue = log_queue
        self.server_sockets = []  # Lista para almacenar los sockets creados (IPv4 e IPv6).


    def enviar_logs(self, tipo, mensaje):
        log_entry = {
            'type': tipo,
            'message': mensaje
        }
        self.log_queue.put(log_entry)

    def start_server(self):
        try:
            addrinfos = socket.getaddrinfo(self.host, self.port, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE)
            n = 0
            for addrinfo in addrinfos:
                print(f"\nAddrinfo {n}: {addrinfo}")
                n += 1
                family, socktype, proto, canonname, sockaddr = addrinfo
                try:
                    server_socket = socket.socket(family, socktype, proto)   
                    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Permite reutilizar la dirección del socket.

                    if family == socket.AF_INET6: # Si la familia es IPv6, se configura un socket que solo acepte conexiones IPv6.
                        server_socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
                        address_type = "IPv6"
                    else: # Si la familia es IPv4, se configura un socket que solo acepte conexiones IPv4.
                        address_type = "IPv4"

                    server_socket.bind(sockaddr)
                    server_socket.listen(5)
                    
                    # Si el socket ya está en la lista de sockets, no se agrega.
                    if server_socket not in self.server_sockets:
                        self.server_sockets.append(server_socket)
                    else:
                        pass

                    print(f"Servidor escuchando en {sockaddr[0]}:{self.port} ({address_type})")
                    self.enviar_logs("INFO", f"Servidor iniciado en {sockaddr[0]}:{self.port} ({address_type})")

                except Exception as e:
                    print(f"Error al crear el socket para {sockaddr}: {e}")
                    self.enviar_logs("ERROR", f"Error al crear el socket para {sockaddr}: {e}")

            if not self.server_sockets:
                raise RuntimeError("No se pudieron crear sockets para ninguna de las direcciones")

            while True:
                try:
                    readable, _, _ = select.select(self.server_sockets, [], []) # Selecciona los sockets que están listos para ser leídos.
                    for s in readable:
                        client_socket, client_address = s.accept()
                        self.contador_clientes += 1
                        print(f"\nCliente {self.contador_clientes} conectado desde {client_address}")
                        self.enviar_logs("INFO", f"Cliente {self.contador_clientes} conectado desde {client_address}")

                        mensaje_bienvenida = f"Cliente {self.contador_clientes}"
                        client_socket.send(mensaje_bienvenida.encode())

                        client_handler = threading.Thread(target=self.manejar_cliente, args=(client_socket,), daemon=True)
                        client_handler.start()
                except KeyboardInterrupt:
                    self.enviar_logs("ERROR", "Servidor cerrado por interrupción de teclado")
                    print("\nInterrupción por teclado detectada. Cerrando el servidor...")
                    break

        except Exception as e:
            print(f"Error al iniciar el servidor: {e}")
            self.enviar_logs("ERROR", f"Error al iniciar el servidor: {e}")

    def manejar_cliente(self, client_socket):
        try:
            while True:
                isbn = client_socket.recv(1024).decode()
                if not isbn or isbn.lower() == 'q':
                    print(f"\nCliente {self.contador_clientes} desconectado ")
                    self.enviar_logs("INFO", f"Cliente {self.contador_clientes} desconectado")
                    break

                if len(isbn) == 13:
                    print(f"\nCódigo ISBN recibido del cliente {self.contador_clientes}: {isbn}") 
                    self.enviar_logs("INFO", f"ISBN recibido: {isbn} del cliente {self.contador_clientes}")

                    scraper = Scraping(isbn)
                    resultados = scraper.concurrent_scraping()

                    if resultados:
                        respuesta = self.obtener_menor_precio(isbn, resultados)
                        client_socket.send(respuesta.encode())
                        print(f"Respuesta enviada al cliente {self.contador_clientes}")
                        self.enviar_logs("INFO", f"Respuesta enviada al cliente {self.contador_clientes}")
                    else:
                        client_socket.send("Error al obtener precios".encode())

                elif len(isbn) != 13:
                    client_socket.send("ISBN no válido".encode())
                    self.enviar_logs("ERROR", f"ISBN no válido proporcionado por el cliente {self.contador_clientes}: {isbn}")
                else:
                    self.enviar_logs("ERROR", f"ISBN no proporcionado por el cliente {self.contador_clientes}")
        except Exception as e:
            print(f"Error al manejar cliente: {e}")
            self.enviar_logs("ERROR", f"Error al manejar cliente: {e}")

    def obtener_menor_precio(self, isbn, resultados):
        resultados_filtrados = []
        for res in resultados:
            if res['precio'] is not None and res['precio'] != 0 and res['libro'] is not None and res['libro'] != "":
                resultados_filtrados.append(res)

        menor_precio = 1000000000

        if len(resultados_filtrados) != 0:
            for resultado in resultados_filtrados:
                if resultado['precio'] < menor_precio:
                    menor_precio = resultado['precio']
                    libreria_conveniente = resultado
            respuesta = f"\nRespuesta del servidor:\n______________________________ BEST SEARCH _______________________________\n\nEl libro se encuentra al mejor precio en {libreria_conveniente['libreria']}:\n\n|---> ISBN13: {isbn}\n|---> TÍTULO: {libreria_conveniente['libro']}\n|---> AUTOR: {libreria_conveniente['autor']}\n|---> PRECIO: ${libreria_conveniente['precio']} ARS\n_________________________________________________________________________\n "
            return respuesta
        else:
            self.enviar_logs("ERROR", f"No se encuentra información del libro código ISBN13: {isbn}")
            return f"\nRespuesta del servidor:\nNo se encuentra información del libro código ISBN13 en ninguna de las librerías: {isbn}"

def start_log_process(log_queue):
    logger = Logs()
    logger.iniciar_logs(log_queue)

if __name__ == "__main__":
    log_queue = Queue()

    log_process = Process(target=start_log_process, args=(log_queue,))
    log_process.start()
    print(f"\nPID del log_process: {log_process.pid}")
    print("PID del servidor:", os.getpid()) 
    server = Servidor(port=5555, log_queue=log_queue)
    server.start_server()

    
    log_queue.put(None)  
    log_process.join()
