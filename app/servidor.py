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
        self.log_queue = log_queue
        self.puerto_cliente = 0
        self.server_sockets = []

    def enviar_logs(self, tipo, mensaje):
        log_entry = {
            'type': tipo,
            'message': mensaje
        }
        self.log_queue.put(log_entry)

    def start_server(self):
        try:
            print("PID del servidor:", os.getpid())
            addrinfos = socket.getaddrinfo(self.host, self.port, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE)

            for addrinfo in addrinfos:
                af, socktype, proto, canonname, sockaddr = addrinfo

                pid = os.fork()
                if pid == 0:
                    print(f'\nProceso Hijo {os.getpid()}')

                    try:
                        server_socket = socket.socket(af, socktype, proto)
                        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                        server_socket.bind(sockaddr)
                        server_socket.listen(5)

                        if af == socket.AF_INET6:
                            address_type = "IPv6"
                        else:
                            address_type = "IPv4"

                        print(f'Servidor  escuchando en {sockaddr} ({address_type})')
                        self.enviar_logs("INFO", f"Servidor iniciado en {sockaddr[0]}:{self.port} ({address_type})")

                        while True:
                            conn, res = server_socket.accept()

                            
                            if af == socket.AF_INET6:
                                print(f'\nCliente conectado usando IPv6 desde {res}')
                                self.enviar_logs("INFO", f'Cliente conectado usando IPv6 desde {res}')
                            
                            elif af == socket.AF_INET:
                                print(f'\nCliente conectado usando IPv4 desde {res}')
                                self.enviar_logs("INFO", f'Cliente conectado usando IPv4 desde {res}')
                            
                            self.puerto_cliente = res[1]

                            mensaje_bienvenida = f"Cliente {self.puerto_cliente}"
                            conn.sendall(mensaje_bienvenida.encode())

                            client_handler = threading.Thread(target=self.manejar_cliente, args=(conn,), daemon=True)
                            client_handler.start()

                    except Exception as e:
                        print(f"Error en el proceso hijo {os.getpid()} al manejar el socket: {e}")
                        self.enviar_logs("ERROR", f"Error en el proceso hijo {os.getpid()} al manejar el socket: {e}")
                    
                    finally:
                        os._exit(0)  # Asegurarse de que el proceso hijo termine

            if not addrinfos:
                raise RuntimeError("No se pudieron crear sockets para ninguna de las direcciones")

        except Exception as e:
            print(f"Error al iniciar el servidor: {e}")
            self.enviar_logs("ERROR", f"Error al iniciar el servidor: {e}")

        # Bucle infinito para mantener el proceso principal activo
        while True:
            pass

    def manejar_cliente(self, client_socket):
        try:
            while True:
                isbn = client_socket.recv(1024).decode()
                if not isbn or isbn.lower() == 'q':
                    print(f"\nCliente {self.puerto_cliente} desconectado ")
                    self.enviar_logs("INFO", f"Cliente {self.puerto_cliente} desconectado")
                    break

                if len(isbn) == 13:
                    print(f"\nCódigo ISBN recibido del cliente {self.puerto_cliente}: {isbn}") 
                    self.enviar_logs("INFO", f"ISBN recibido: {isbn} del cliente {self.puerto_cliente}")

                    scraper = Scraping(isbn)
                    resultados = scraper.concurrent_scraping()

                    if resultados:
                        respuesta = self.obtener_menor_precio(isbn, resultados)
                        client_socket.send(respuesta.encode())
                        print(f"Respuesta enviada al cliente {self.puerto_cliente}")
                        self.enviar_logs("INFO", f"Respuesta enviada al cliente {self.puerto_cliente}")
                    else:
                        client_socket.send("Error al obtener precios".encode())

                elif len(isbn) != 13:
                    client_socket.send("ISBN no válido".encode())
                    self.enviar_logs("ERROR", f"ISBN no válido proporcionado por el cliente {self.puerto_cliente}: {isbn}")
                else:
                    self.enviar_logs("ERROR", f"ISBN no proporcionado por el cliente {self.puerto_cliente}")
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

    # Iniciar el proceso de logs como un proceso separado usando multiprocessing
    log_process = Process(target=start_log_process, args=(log_queue,))
    log_process.start()
    print(f"PID del log_process: {log_process.pid}")
    print("PID del PP:", os.getpid())


    # Iniciar servidor
    server = Servidor(port=5555, log_queue=log_queue)
    server.start_server()

    log_queue.put(None)  # Señal para terminar el proceso de logs
    log_process.join()