# from multiprocessing import Process, Queue
# import socket
# from concurrent.futures import ThreadPoolExecutor
# import requests
# from logs import Logs  # Actualizado
# from libreria import Libreria as Lib
# import os
# import threading

# session = requests.Session()

# class Scraping:
#     def __init__(self, isbn):
#         self.isbn = isbn

#     def cuspide_page_response(self):
#         try:
#             response = session.get(Lib(self.isbn).cuspide_url)
#             if response.status_code == 200:
#                 print("Scrapeando Cuspide")
#                 informacion_cuspide = Lib(self.isbn).scrap_cuspide(session)
#                 return informacion_cuspide
#         except Exception as e:
#             print(f"Error al scrapear Cuspide: {e}")
#             return {'isbn': self.isbn, 'libro': None, 'autor': None ,'precio': None, 'libreria': 'Cúspide'}

#     def casassa_page_response(self):
#         try:
#             response = session.get(Lib(self.isbn).casassa_url)
#             if response.status_code == 200:
#                 print("Scrapeando Casassa")
#                 informacion_casassa = Lib(self.isbn).scrap_casassa(session)
#                 return informacion_casassa
#         except Exception as e:
#             print(f"Error al scrapear Casassa: {e}")
#             return {'isbn': self.isbn, 'libro': None, 'autor': None ,'precio': None, 'libreria': 'Casassa y Lorenzo'}

#     def sbs_page_response(self):
#         try:
#             response = session.get(Lib(self.isbn).sbs_url)
#             if response.status_code == 200:
#                 print("Scrapeando SBS")
#                 informacion_sbs = Lib(self.isbn).scrap_sbs(session)
#                 return informacion_sbs
#         except Exception as e:
#             print(f"Error al scrapear SBS: {e}")
#             return {'isbn': self.isbn, 'libro': None, 'autor': None ,'precio': None, 'libreria': 'Sbs'}

#     def concurrent_scraping(self):
#         try:
#             with ThreadPoolExecutor(max_workers=3) as executor:
#                 future1 = executor.submit(self.cuspide_page_response)
#                 future2 = executor.submit(self.casassa_page_response)
#                 future3 = executor.submit(self.sbs_page_response)

#                 resultados = [
#                     future1.result(),
#                     future2.result(),
#                     future3.result()
#                 ]
#                 return resultados
#         except Exception as e:
#             print(f"Error en concurrent_scraping: {e}")
#             return None


# class Servidor:
#     def __init__(self, host='localhost', port=5000, log_queue=None):
#         self.host = host
#         self.port = port
#         self.contador_clientes = 0
#         self.log_queue = log_queue
#         self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#     def enviar_logs(self, tipo, mensaje):
#         log_entry = {
#             'type': tipo,
#             'message': mensaje
#         }
#         self.log_queue.put(log_entry)

#     def start_server(self):
#         self.server_socket.bind((self.host, self.port))
#         self.server_socket.listen(5)
#         print(f"Servidor escuchando en {self.host}:{self.port}")
#         self.enviar_logs("INFO", f"Servidor iniciado en {self.host}:{self.port}")
#         print('Servidor PID', os.getpid())

#         while True:
#             client_socket, client_address = self.server_socket.accept()
#             self.contador_clientes += 1
#             print(f"Cliente {self.contador_clientes} conectado desde {client_address}")
#             self.enviar_logs("INFO", f"Cliente {self.contador_clientes} conectado desde {client_address}")

#             mensaje_bienvenida = f"Cliente {self.contador_clientes}"
#             client_socket.send(mensaje_bienvenida.encode())

#             # Con hilos
#             client_handler = Process(target=self.manejar_cliente, args=(client_socket,))
#             client_handler.start()

#             client_socket.close()

#     def manejar_cliente(self, client_socket):
#         try:
#             while True:
#                 isbn = client_socket.recv(1024).decode()
#                 if not isbn or isbn.lower() == 'q':
#                     print(f"Cliente {self.contador_clientes} desconectado ")
#                     self.enviar_logs("INFO", f"Cliente {self.contador_clientes} desconectado")
#                     break

#                 if len(isbn) == 13:
#                     print(f"Recibido ISBN: {isbn}")
#                     self.enviar_logs("INFO", f"ISBN recibido: {isbn} del cliente {self.contador_clientes}")

#                     scraper = Scraping(isbn)
#                     resultados = scraper.concurrent_scraping()

#                     if resultados:
#                         respuesta = self.obtener_menor_precio(isbn, resultados)
#                         client_socket.send(respuesta.encode())
#                         print(f"Enviado al cliente: {respuesta}")
#                         self.enviar_logs("INFO", f"Respuesta enviada al cliente {self.contador_clientes}")
#                     else:
#                         client_socket.send("Error al obtener precios".encode())

#                 elif len(isbn) != 13:
#                     client_socket.send("ISBN no válido".encode())
#                     self.enviar_logs("ERROR", f"ISBN no válido proporcionado por el cliente {self.contador_clientes}: {isbn}")
#                 else:
#                     client_socket.send("ISBN no proporcionado".encode())
#                     self.enviar_logs("ERROR", f"ISBN no proporcionado por el cliente {self.contador_clientes}")
#         except Exception as e:
#             print(f"Error al manejar cliente: {e}")
#             self.enviar_logs("ERROR", f"Error al manejar cliente: {e}")

#     def obtener_menor_precio(self, isbn, resultados):
#         resultados_filtrados = []
#         for res in resultados:
#             if res['precio'] is not None and res['precio'] != 0 and res['libro'] is not None and res['libro'] != "":
#                 resultados_filtrados.append(res)

#         menor_precio = 1000000000

#         if len(resultados_filtrados) != 0:
#             for resultado in resultados_filtrados:
#                 if resultado['precio'] < menor_precio:
#                     menor_precio = resultado['precio']
#                     libreria_conveniente = resultado
#             respuesta = f"\nRespuesta del servidor:\n______________________________ BEST SEARCH _______________________________\n\nEl libro se encuentra al mejor precio en {libreria_conveniente['libreria']}:\n\n|---> ISBN13: {isbn}\n|---> TÍTULO: {libreria_conveniente['libro']}\n|---> AUTOR: {libreria_conveniente['autor']}\n|---> PRECIO: ${libreria_conveniente['precio']} ARS\n_________________________________________________________________________\n "
#             return respuesta
#         else:
#             self.enviar_logs("ERROR", f"No se encuentra información del libro código ISBN13: {isbn}")
#             return f"\nRespuesta del servidor:\nNo se encuentra información del libro código ISBN13 en ninguna de las librerías: {isbn}"

# def start_log_process(log_queue):
#     logger = Logs()
#     logger.iniciar_logs(log_queue)

# if __name__ == "__main__":
#     log_queue = Queue()

#     # Iniciar el proceso de logs como un proceso separado usando multiprocessing
#     log_process = Process(target=start_log_process, args=(log_queue,))
#     log_process.start()
#     print(f"PID del log_process: {log_process.pid}")

#     # Iniciar servidor
#     server = Servidor(port=5005, log_queue=log_queue)
#     server.start_server()

#     log_queue.put(None)  # Señal para terminar el proceso de logs
#     log_process.join()


from multiprocessing import Process, Queue
import socket
from concurrent.futures import ThreadPoolExecutor
import requests
from logs import Logs  # Actualizado
from libreria import Libreria as Lib
import os
import threading
import select

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
    def __init__(self, host='localhost', port=5000, log_queue=None):
        self.host = host
        self.port = port
        self.contador_clientes = 0
        self.log_queue = log_queue
        self.server_socket_ipv4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket_ipv6 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

    def enviar_logs(self, tipo, mensaje):
        log_entry = {
            'type': tipo,
            'message': mensaje
        }
        self.log_queue.put(log_entry)

    def start_server(self):
        self.server_socket_ipv4.bind(('0.0.0.0', self.port))
        self.server_socket_ipv6.bind(('::', self.port))
        self.server_socket_ipv4.listen(5)
        self.server_socket_ipv6.listen(5)
        print(f"Servidor escuchando en {self.host}:{self.port} (IPv4 e IPv6)")
        self.enviar_logs("INFO", f"Servidor iniciado en {self.host}:{self.port} (IPv4 e IPv6)")
        print('Servidor PID', os.getpid())

        sockets = [self.server_socket_ipv4, self.server_socket_ipv6]

        while True:
            readable, _, _ = select.select(sockets, [], [])
            for s in readable:
                client_socket, client_address = s.accept()
                self.contador_clientes += 1
                print(f"Cliente {self.contador_clientes} conectado desde {client_address}")
                self.enviar_logs("INFO", f"Cliente {self.contador_clientes} conectado desde {client_address}")

                mensaje_bienvenida = f"Cliente {self.contador_clientes}"
                client_socket.send(mensaje_bienvenida.encode())

                # Con hilos
                client_handler = Process(target=self.manejar_cliente, args=(client_socket,))
                client_handler.start()

                client_socket.close()

    def manejar_cliente(self, client_socket):
        try:
            while True:
                isbn = client_socket.recv(1024).decode()
                if not isbn or isbn.lower() == 'q':
                    print(f"Cliente {self.contador_clientes} desconectado ")
                    self.enviar_logs("INFO", f"Cliente {self.contador_clientes} desconectado")
                    break

                if len(isbn) == 13:
                    print(f"Recibido ISBN: {isbn}")
                    self.enviar_logs("INFO", f"ISBN recibido: {isbn} del cliente {self.contador_clientes}")

                    scraper = Scraping(isbn)
                    resultados = scraper.concurrent_scraping()

                    if resultados:
                        respuesta = self.obtener_menor_precio(isbn, resultados)
                        client_socket.send(respuesta.encode())
                        print(f"Enviado al cliente: {respuesta}")
                        self.enviar_logs("INFO", f"Respuesta enviada al cliente {self.contador_clientes}")
                    else:
                        client_socket.send("Error al obtener precios".encode())

                elif len(isbn) != 13:
                    client_socket.send("ISBN no válido".encode())
                    self.enviar_logs("ERROR", f"ISBN no válido proporcionado por el cliente {self.contador_clientes}: {isbn}")
                else:
                    client_socket.send("ISBN no proporcionado".encode())
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

    # Iniciar el proceso de logs como un proceso separado usando multiprocessing
    log_process = Process(target=start_log_process, args=(log_queue,))
    log_process.start()
    print(f"PID del log_process: {log_process.pid}")

    # Iniciar servidor
    server = Servidor(port=5005, log_queue=log_queue)
    server.start_server()

    log_queue.put(None)  # Señal para terminar el proceso de logs
    log_process.join()