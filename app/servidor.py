import socket
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
import requests
import logging
import threading
from libreria import Libreria as Lib

# Ejemplo de ISBN: 9789501298321
# Falta que el servidor maneje múltiples conexiones de clientes, tira error
# Manejar bien el cliente, los log y las excepciones. Verificar que los logs son un proceso separado

class Scraping:
    def __init__(self, isbn):
        self.isbn = isbn
        self.queue = Queue()

    def cuspide_page_response(self):
        try:
            response = session.get(Lib(self.isbn).cuspide_url)
            if response.status_code == 200:
                print("Scrapeando Cuspide")
                self.queue.put(response)
                informacion_cuspide = Lib(self.isbn).scrap_cuspide(session)
                print(informacion_cuspide)
                return informacion_cuspide
        except Exception as e:
            print(f"Error al scrapear Cuspide: {e}")
            return None

    def casassa_page_response(self):
        try:
            response = session.get(Lib(self.isbn).casassa_url)
            if response.status_code == 200:
                print("Scrapeando Casassa")
                self.queue.put(response)
                informacion_casassa = Lib(self.isbn).scrap_casassa(session)
                print(informacion_casassa)
                return informacion_casassa
        except Exception as e:
            print(f"Error al scrapear Casassa: {e}")
            return None

    def sbs_page_response(self):
        try:
            response = session.get(Lib(self.isbn).sbs_url)
            if response.status_code == 200:
                print("Scrapeando SBS")
                self.queue.put(response)
                informacion_sbs = Lib(self.isbn).scrap_sbs(session)
                print(informacion_sbs)
                return informacion_sbs
        except Exception as e:
            print(f"Error al scrapear SBS: {e}")
            return None

    def concurrent_scraping(self):
        try:
            with ThreadPoolExecutor(max_workers=3) as executor:
                future1 = executor.submit(self.cuspide_page_response)
                future2 = executor.submit(self.casassa_page_response)
                future3 = executor.submit(self.sbs_page_response)

                # Esperamos a que terminen las 3 tareas
                results = [
                    future1.result(),
                    future2.result(),
                    future3.result()
                ]
                return results
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
        self.logs = Logs()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start_server(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Servidor escuchando en {self.host}:{self.port}")
        self.logs.log_info(f"Servidor iniciado en {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Cliente conectado desde {client_address}")
            self.logs.log_info(f"Cliente conectado desde {client_address}")

            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

    def handle_client(self, client_socket):
        try:
            isbn = client_socket.recv(1024).decode()
            if len(isbn) == 13:
                print(f"Recibido ISBN: {isbn}")
                self.logs.log_info(f"ISBN recibido: {isbn}")

                scraper = Scraping(isbn)
                results = scraper.concurrent_scraping()

                if results:
                    min_price_info = min((res for res in results if res is not None), key=lambda x: x['price'])
                    response = f"El menor precio es {min_price_info['price']} en la librería {min_price_info['store']}"
                    client_socket.send(response.encode())
                    print(f"Enviado al cliente: {response}")
                    self.logs.log_info(f"Enviado al cliente: {response}")
                else:
                    client_socket.send("Error al obtener precios".encode())
                    self.logs.log_error(f"Error al obtener precios para el ISBN: {isbn}")
            elif len(isbn) != 13:
                client_socket.send("ISBN no válido".encode())
                self.logs.log_error(f"ISBN no válido proporcionado por el cliente: {isbn}")
            else:
                client_socket.send("ISBN no proporcionado".encode())
                self.logs.log_error("ISBN no proporcionado por el cliente")
        except Exception as e:
            print(f"Error al manejar cliente: {e}, se cerrará el servidor")
            self.logs.log_error(f"Error al manejar cliente: {e}")
            self.server_socket.close()

        finally:
            client_socket.close()

if __name__ == "__main__":
    session = requests.Session()
    server = Servidor(port=5005)
    server.start_server()
