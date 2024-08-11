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
                print(f"Scrapeando Cuspide")
                self.queue.put(response)
                informacion_cuspide =Lib(isbn).scrap_cuspide(session)  
                print(informacion_cuspide) 
                return informacion_cuspide
        except Exception as e:
            print(f"Error  al scrapear: {e}")
            return None

    def casassa_page_response(self, isbn, session):
        try:
            response = session.get(Lib(isbn).casassa_url)
            if response.status_code == 200:        
                print(f"Scrapeando Casassa")
                self.queue.put(response)
                informacion_casassa =Lib(isbn).scrap_casassa(session)  
                print(informacion_casassa)
                return informacion_casassa
        except Exception as e:
            print(f"Error  al scrapear: {e}")
            return None

    def sbs_page_response(self, isbn, session):
        try:
            response = session.get(Lib(isbn).sbs_url)
            if response.status_code == 200:        
                print(f"Scrapeando SBS")
                self.queue.put(response)
                informacion_sbs = Lib(isbn).scrap_sbs(session)  
                print(informacion_sbs)
                return informacion_sbs
        except Exception as e:
            print(f"Error  al scrapear: {e}")
            return None

    def concurrent_scraping(self, isbn, session):
        try:
            with ThreadPoolExecutor(max_workers=3) as executor:
                future1 = executor.submit(self.cuspide_page_response, isbn, session)
                future2 = executor.submit(self.casassa_page_response, isbn, session)
                future3 = executor.submit(self.sbs_page_response, isbn, session)
        
                # Esperamos a que terminen las 3 tareas
                future1.result()
                future2.result()
                future3.result()
        except Exception as e:
            print(f"Error en concurrent_scraping: {e}")



ScrapingServer().concurrent_scraping(9789501298321, session)






