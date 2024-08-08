import concurrent.futures
import requests
from queue import Queue
import socketserver
import socket
import threading
from concurrent.futures import ThreadPoolExecutor
from libreria import Libreria as Lib

session = requests.Session()

class ScrapingServer:
    
    def cuspide_page_response(self, isbn, session):
        try:
            response = session.get(Lib(isbn).cuspide_url)
            if response.status_code == 200:        
                print(f"Scrapeando")
                Lib(isbn).scrap_cuspide(session)  
        except Exception as e:
            print(f"Error  al scrapear: {e}")
    
    def casassa_page_response(self, isbn, session):
        try:
            response = session.get(Lib(isbn).casassa_url)
            if response.status_code == 200:        
                print(f"Scrapeando")
                Lib(isbn).scrap_casassa(session)  
        except Exception as e:
            print(f"Error  al scrapear: {e}")
    
    def sbs_page_response(self, isbn, session):
        try:
            response = session.get(Lib(isbn).sbs_url)
            if response.status_code == 200:        
                print(f"Scrapeando")
                Lib(isbn).scrap_sbs(session)  
        except Exception as e:
            print(f"Error  al scrapear: {e}")
    
    def concurrent_scraping(self, isbn, session):
        try:
            with ThreadPoolExecutor(max_workers=3) as executor:
                future1 = executor.submit(self.cuspide_page_response, isbn, session)
                # future2 = self.executor.submit(self.casassa_page_response, isbn, session)
                # future3 = self.executor.submit(self.sbs_page_response, isbn, session)
        
                # Espera a que ambas tareas terminen
                future1.result()
                # future2.result()
        except Exception as e:
            print(f"Error en concurrent_scraping: {e}")
        
ScrapingServer().concurrent_scraping(9789504988014, session)




# # Función para manejar la cola de URLs
# def worker(queue, results):
#     while not queue.empty():
#         url = queue.get()
#         if url is None:
#             break
#         page_response(url, results)
#         queue.task_done()

# # Lista de URLs a ser scrapeadas
# urls = [
#     'https://example.com',
#     'https://example.org',
#     'https://example.net'
#     # Agrega más URLs según sea necesario
# ]

# # Crear una cola y llenar con las URLs
# queue = Queue()
# for url in urls:
#     queue.put(url)

# # Diccionario para almacenar los resultados
# results = {}

# # Usar ThreadPoolExecutor para manejar múltiples hilos
# with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
#     futures = [executor.submit(worker, queue, results) for _ in range(5)]

# # Esperar a que todas las tareas se completen
# queue.join()

# # Imprimir resultados
# for url, result in results.items():
#     print(f"{url}: {result}")

# print("All tasks completed.")
