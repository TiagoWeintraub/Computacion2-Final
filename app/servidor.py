import socket
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
import requests
import logging
from libreria import Libreria as Lib
from multiprocessing import Process

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
                # print(informacion_cuspide)
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
                # print(informacion_casassa)
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
                # print(informacion_sbs)
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

                # Esperamos a que terminen las 3 tareas
                resultados = [
                    future1.result(),
                    future2.result(),
                    future3.result()
                ]
                return resultados
        except Exception as e:
            print(f"Error en concurrent_scraping: {e}")
            return None

class Logs:
    def __init__(self, log_file="server.log"):
        logging.basicConfig(filename=log_file, level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger()

    def log_info(self, message):
        self.logger.info(message)

    def log_error(self, message):
        self.logger.error(message)


class Servidor:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.contador_clientes = 0
        self.logs = Logs()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start_server(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Servidor escuchando en {self.host}:{self.port}")
        self.logs.log_info(f"Servidor iniciado en {self.host}:{self.port}")
        print(f"Clientes Conectados: {self.contador_clientes}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            self.contador_clientes += 1
            print(f"Cliente {self.contador_clientes} conectado desde {client_address}")
            print(f"Clientes Conectados: {self.contador_clientes}")
            self.logs.log_info(f"Cliente {self.contador_clientes} conectado desde {client_address}")
            self.logs.log_info(f"Clientes Conectados: {self.contador_clientes}")

            mensaje_bienvenida = f"Cliente {self.contador_clientes}" # Mensaje de bienvenida al cliente
            client_socket.send(mensaje_bienvenida.encode())

            client_handler = Process(target=self.manejar_cliente, args=(client_socket,)) # Crear un nuevo proceso para manejar el cliente
            client_handler.start()

            # Cerrar el socket en el proceso principal, el proceso hijo lo manejará
            client_socket.close()

    def manejar_cliente(self, client_socket):
        try:
            while True:
                isbn = client_socket.recv(1024).decode()
                if not isbn:
                    print(f"Cliente {self.contador_clientes} desconectado ")
                    self.logs.log_info(f"Cliente {self.contador_clientes} desconectado")
                    self.contador_clientes -= 1
                    print(f"Clientes Conectados: {self.contador_clientes}")
                    break
                
                if len(isbn) == 13:
                    print(f"Recibido ISBN: {isbn}")
                    self.logs.log_info(f"ISBN recibido: {isbn}")

                    scraper = Scraping(isbn)
                    resultados = scraper.concurrent_scraping()

                    if resultados:
                        respuesta = self.obtener_menor_precio(isbn, resultados)
                        client_socket.send(respuesta.encode())
                        print(f"Enviado al cliente: {respuesta}")
                        self.logs.log_info(f"Enviado al cliente {self.contador_clientes}: {respuesta}")
                    else:
                        client_socket.send("Error al obtener precios".encode())
                        self.logs.log_error(f"Error al obtener precios para el ISBN: {isbn}, Cliente {self.contador_clientes}")
                elif len(isbn) != 13:
                    client_socket.send("ISBN no válido".encode())
                    self.logs.log_error(f"ISBN no válido proporcionado por el cliente {self.contador_clientes}: {isbn}")
                else:
                    client_socket.send("ISBN no proporcionado".encode())
                    self.logs.log_error(f"ISBN no proporcionado por el cliente {self.contador_clientes}")
        except Exception as e:
            print(f"Error al manejar cliente: {e}")
            self.logs.log_error(f"Error al manejar cliente: {e}")
        # finally:
        #     client_socket.close()
        
    def obtener_menor_precio(self, isbn, resultados):
        resultados_filtrados = []
        for res in resultados:
            if res['precio'] is not None and res['precio'] != 0:
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
            self.logs.log_error(f"No se encuentra información del libro código ISBN13: {isbn}")
            return f"\nRespuesta del servidor:\nNo se encuentra información del libro código ISBN13 en ninguna de las librerías: {isbn}"


if __name__ == "__main__":

    server = Servidor(port=5005)
    server.start_server()
