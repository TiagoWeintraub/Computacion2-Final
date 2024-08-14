import requests
from queue import Queue
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
                # print(informacion_cuspide) 
                return informacion_cuspide
        except Exception as e:
            print(f"Error  al scrapear: {e}")
            return {'isbn': isbn, 'libro': None, 'autor': None ,'precio': None, 'libreria': 'Cúspide'}

    def casassa_page_response(self, isbn, session):
        try:
            response = session.get(Lib(isbn).casassa_url)
            if response.status_code == 200:        
                print(f"Scrapeando Casassa")
                self.queue.put(response)
                informacion_casassa =Lib(isbn).scrap_casassa(session)  
                # print(informacion_casassa)
                return informacion_casassa
        except Exception as e:
            print(f"Error  al scrapear: {e}")
            return {'isbn': isbn, 'libro': None, 'autor': None ,'precio': None, 'libreria': 'Casassa y Lorenzo'}

    def sbs_page_response(self, isbn, session):
        try:
            response = session.get(Lib(isbn).sbs_url)
            if response.status_code == 200:        
                print(f"Scrapeando SBS")
                self.queue.put(response)
                informacion_sbs = Lib(isbn).scrap_sbs(session)  
                # print(informacion_sbs)
                return informacion_sbs
        except Exception as e:
            print(f"Error  al scrapear: {e}")
            return {'isbn': isbn, 'libro': None, 'autor': None ,'precio': None, 'libreria': 'Sbs'}

    def concurrent_scraping(self, isbn, session):
        try:
            with ThreadPoolExecutor(max_workers=3) as executor:
                future1 = executor.submit(self.cuspide_page_response, isbn, session)
                future2 = executor.submit(self.casassa_page_response, isbn, session)
                future3 = executor.submit(self.sbs_page_response, isbn, session)
        
                # Esperamos a que terminen las 3 tareas
                resultados =[future1.result(), future2.result(), future3.result()]
                return resultados
        except Exception as e:
            print(f"Error en concurrent_scraping: {e}")
            
    def obtener_menor_precio(self, isbn, resultados):
        resultados_filtrados = []
        for res in resultados:
            print('Resultadooo: ',res)
            if res['precio'] is not None and res['precio'] != 0:
                resultados_filtrados.append(res)

        menor_precio = 1000000000
        
        if len(resultados_filtrados) != 0:
            for resultado in resultados_filtrados:
                if resultado['precio'] < menor_precio:
                    menor_precio = resultado['precio']
                    libreria_conveniente = resultado
            print('CONVIENE ESTA ',libreria_conveniente)
            return libreria_conveniente

        else:
            return f"No se encuentra información del libro código ISBN13: {isbn}"
        
            # if res is not None and res['precio'] is not None and res['precio'] != 0:
            #     print(res)
            #     resultados_filtrados.append(res)
            # else:
            #     print(f"No se encuentra información del libro código ISBN13: {isbn}") 
            #     # self.logs.log_error(f"No se encuentra información del libro código ISBN13: {isbn}")
            #     return f"No se encuentra información del libro código ISBN13: {isbn}"

        # if len(resultados_filtrados) != 0:
        #     menor_precio = resultados_filtrados[0]  # Arranca con el primer resultado
        #     for resultado in resultados_filtrados:
        #         if resultado['precio'] < menor_precio['precio']:
        #             menor_precio = resultado
        #     return f"El precio más bajo es de {menor_precio['precio']} en {menor_precio['libreria']}"
        
        # else:
        #     return "No se encuentra información del libro código ISBN13: {isbn}"

isbn = 9789876137782 # 9789607706669
resultados = ScrapingServer().concurrent_scraping(isbn, session)

respuesta = ScrapingServer().obtener_menor_precio(isbn, resultados)

print(respuesta)




