import logging
from multiprocessing import Process, Queue
import socket
from concurrent.futures import ThreadPoolExecutor
import requests
from logs import Logs
from libreria import Libreria as Lib

session = requests.Session()

class QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        # Crear un diccionario con la información del log
        log_entry = {
            'type': record.levelname,
            'message': self.format(record)
        }
        self.log_queue.put(log_entry)



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
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Configurar el logger en el proceso del servidor
        queue_handler = QueueHandler(self.log_queue)
        queue_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(queue_handler)

    def enviar_logs(self, tipo, mensaje):
        if tipo == 'INFO':
            self.logger.info(mensaje)
        elif tipo == 'ERROR':
            self.logger.error(mensaje)

    def start_server(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Servidor escuchando en {self.host}:{self.port}")
        self.enviar_logs("INFO", f"Servidor iniciado en {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            self.contador_clientes += 1
            print(f"Cliente {self.contador_clientes} conectado desde {client_address}")

            self.enviar_logs("INFO", f"Cliente {self.contador_clientes} conectado desde {client_address}")
            self.enviar_logs("INFO", f"Clientes Conectados: {self.contador_clientes}")

            mensaje_bienvenida = f"Cliente {self.contador_clientes}"
            client_socket.send(mensaje_bienvenida.encode())

            client_handler = Process(target=self.manejar_cliente, args=(client_socket,))
            client_handler.start()

            client_socket.close()

    def manejar_cliente(self, client_socket):
        try:
            while True:
                isbn = client_socket.recv(1024).decode()
                if not isbn:
                    print(f"Cliente {self.contador_clientes} desconectado ")
                    self.enviar_logs("INFO", f"Cliente {self.contador_clientes} desconectado")
                    self.contador_clientes -= 1
                    break

                if len(isbn) == 13:
                    print(f"Recibido ISBN: {isbn}")
                    self.enviar_logs("INFO", f"ISBN recibido: {isbn}")

                    scraper = Scraping(isbn)
                    resultados = scraper.concurrent_scraping()

                    if resultados:
                        respuesta = self.obtener_menor_precio(isbn, resultados)
                        client_socket.send(respuesta.encode())
                        print(f"Enviado al cliente: {respuesta}")
                        self.enviar_logs("INFO", f"Enviado al cliente {self.contador_clientes}: {respuesta}")
                    else:
                        client_socket.send("Error al obtener precios".encode())
                        self.enviar_logs("ERROR", f"Error al obtener precios para el ISBN: {isbn}, Cliente {self.contador_clientes}")
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
            self.enviar_logs("ERROR",f"No se encuentra información del libro código ISBN13: {isbn}")
            return f"\nRespuesta del servidor:\nNo se encuentra información del libro código ISBN13 en ninguna de las librerías: {isbn}"


if __name__ == "__main__":
    log_queue = Queue()

    # Crear un proceso para manejar los logs
    logger = Logs()
    log_process = logger.iniciar_logs(log_queue)

    # Iniciar servidor
    server = Servidor(port=5005, log_queue=log_queue)
    server.start_server()

    log_process.join()
