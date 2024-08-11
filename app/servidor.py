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
                future3 = executor.submit(self.sbs_page_response, isbn, session)
        
                # Espera a que ambas tareas terminen
                future1.result()
                future2.result()
                future3.result()
        except Exception as e:
            print(f"Error en concurrent_scraping: {e}")
    
    
        
ScrapingServer().concurrent_scraping(9789501298321, session)






