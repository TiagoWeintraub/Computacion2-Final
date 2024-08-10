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
    
    
    def __init__(self):
        self.queue = Queue()
    
    
    def cuspide_page_response(self, isbn, session):
        try:
            response = session.get(Lib(isbn).cuspide_url)
            if response.status_code == 200:        
                print(f"Scrapeando")
                self.queue.put(response)
                Lib(isbn).scrap_cuspide(session)  
        except Exception as e:
            print(f"Error  al scrapear: {e}")
    
    def casassa_page_response(self, isbn, session):
        try:
            response = session.get(Lib(isbn).casassa_url)
            if response.status_code == 200:        
                print(f"Scrapeando")
                self.queue.put(response)
                Lib(isbn).scrap_casassa(session)  
        except Exception as e:
            print(f"Error  al scrapear: {e}")
    
    def sbs_page_response(self, isbn, session):
        try:
            response = session.get(Lib(isbn).sbs_url)
            if response.status_code == 200:        
                print(f"Scrapeando")
                self.queue.put(response)
                Lib(isbn).scrap_sbs(session)  
        except Exception as e:
            print(f"Error  al scrapear: {e}")
    
    def concurrent_scraping(self, isbn, session):
        try:
            with ThreadPoolExecutor(max_workers=3) as executor:
                future1 = executor.submit(self.cuspide_page_response, isbn, session)
                future2 = executor.submit(self.casassa_page_response, isbn, session)
                # future3 = executor.submit(self.sbs_page_response, isbn, session)
        
                # Espera a que ambas tareas terminen
                future1.result()
                future2.result()
                # future3.result()
        except Exception as e:
            print(f"Error en concurrent_scraping: {e}")
    
    
        
ScrapingServer().concurrent_scraping(9789504988014, session)









# import concurrent.futures
# import requests
# from queue import Queue
# from concurrent.futures import ThreadPoolExecutor
# from libreria import Libreria as Lib

# session = requests.Session()

# class ScrapingServer:
#     def __init__(self):
#         self.queue = Queue()
    
#     def cuspide_page_response(self, isbn, session):
#         try:
#             response = session.get(Lib(isbn).cuspide_url)
#             if response.status_code == 200:
#                 print(f"Scrapeando Cúspide")
#                 self.queue.put(('cuspide', response))
#         except Exception as e:
#             print(f"Error al scrapear Cúspide: {e}")
    
#     def casassa_page_response(self, isbn, session):
#         try:
#             response = session.get(Lib(isbn).casassa_url)
#             if response.status_code == 200:
#                 print(f"Scrapeando Casassa")
#                 self.queue.put(('casassa', response))
#         except Exception as e:
#             print(f"Error al scrapear Casassa: {e}")
    
#     def sbs_page_response(self, isbn, session):
#         try:
#             response = session.get(Lib(isbn).sbs_url)
#             if response.status_code == 200:
#                 print(f"Scrapeando SBS")
#                 self.queue.put(('sbs', response))
#         except Exception as e:
#             print(f"Error al scrapear SBS: {e}")
    
#     def concurrent_scraping(self, isbn, session):
#         try:
#             with ThreadPoolExecutor(max_workers=3) as executor:
#                 futures = [
#                     executor.submit(self.cuspide_page_response, isbn, session),
#                     executor.submit(self.casassa_page_response, isbn, session),
#                     executor.submit(self.sbs_page_response, isbn, session)
#                 ]
                
#                 # Esperar que todas las tareas terminen
#                 for future in futures:
#                     future.result()
#         except Exception as e:
#             print(f"Error en concurrent_scraping: {e}")
    
#     def process_queue(self):
#         while not self.queue.empty():
#             store, response = self.queue.get()
#             print(f"Procesando respuesta de {store}")
#             try:
#                 if store == 'cuspide':
#                     Lib(response.url).scrap_cuspide(session)
#                 elif store == 'casassa':
#                     Lib(response.url).scrap_casassa(session)
#                 elif store == 'sbs':
#                     Lib(response.url).scrap_sbs(session)
#             except Exception as e:
#                 print(f"Error procesando {store}: {e}")

# # Uso del ScrapingServer
# isbn = "9789504988014"
# server = ScrapingServer()
# server.concurrent_scraping(isbn, session)
# server.process_queue()
# ScrapingServer().concurrent_scraping(9789504988014, session)






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
