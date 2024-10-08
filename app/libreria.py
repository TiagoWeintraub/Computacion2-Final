from bs4 import BeautifulSoup
import json

class Libreria:
    def __init__(self, isbn):
        self.isbn = isbn
        self.informacion_cuspide = {'isbn': isbn, 'libro': '', 'autor': '' ,'precio': '', 'libreria': 'CÚSPIDE'}
        self.informacion_casassa = {'isbn': isbn, 'libro': '', 'autor': '' ,'precio': '', 'libreria': 'CASASSA Y LORENZO'}
        self.informacion_sbs = {'isbn': isbn, 'libro': '', 'autor': '' ,'precio': '', 'libreria': 'SBS'}
        self.cuspide_url = f"https://cuspide.com/?s={isbn}&post_type=product"
        self.casassa_url = f"https://www.casassaylorenzo.com/resultados.aspx?c={isbn}&por=isbn"
        self.sbs_url = f"https://www.sbs.com.ar/{isbn}"

    def scrap_cuspide(self, session):
        response = session.get(self.cuspide_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            titulo = soup.find('h1', class_='product-title product_title entry-title')
            if titulo:
                try: # Titulo libro 1
                    titulo_restante = soup.find('div', style='max-width: 400px; display: inline-block;')
                    if titulo_restante:
                        titulo_formateado = str(titulo.text.strip("\n\t"))
                        titulo_restante = str(titulo_restante.text.strip("\n\t"))
                        titulo_completo = titulo_formateado + ". " + titulo_restante
                        self.informacion_cuspide['libro'] = titulo_completo
                    else:
                        titulo_formateado = str(titulo.text.strip("\n\t"))
                        self.informacion_cuspide['libro'] = titulo_formateado
                except Exception as e:
                    self.informacion_cuspide['libro'] = None

                try: # Autor 2
                    div_autor = soup.find('div', class_='product-info summary col-fit col entry-summary product-summary text-left form-minimal')
                    autor = div_autor.find('span', style='font-size: 14px;')
                    limpiando_autor = autor.text.strip()
                    self.informacion_cuspide['autor'] = limpiando_autor 
                except Exception as e:
                    self.informacion_cuspide['autor'] = None

                try: # Precio 3
                    precio = soup.find('p', class_='price product-page-price')
                    precio_formateado = str(precio.text.strip("\n$\xa0"))
                    precio_formateado = precio_formateado.replace(".", "")
                    precio_formateado = precio_formateado.replace(",", ".")
                    self.informacion_cuspide['precio'] = float(str(precio_formateado))
                except Exception as e:
                    self.informacion_cuspide['precio'] = None

            else:
                self.informacion_cuspide = {'isbn': self.isbn, 'libro': None, 'autor': None ,'precio': None, 'libreria': 'Cúspide'}
            
            # print("Cuspide: ", self.informacion_cuspide)
            return self.informacion_cuspide
        else:
            print(f"Error en la respuesta de la página Cuspide: {response.status_code}")
            self.informacion_cuspide = {'isbn': self.isbn, 'libro': None, 'autor': None ,'precio': None, 'libreria': 'Cúspide'}


    def scrap_casassa(self, session):
        response = session.get(self.casassa_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            titulo = soup.find('a', id='ContentPlaceHolderContenido_resultadosItems_rptResultados_a_titulo_0')
            if titulo:
                try: #BUSCAMOS TITULO 
                    titulo_formateado = str(titulo.text.strip("\n\t"))
                    self.informacion_casassa['libro'] = titulo_formateado
                except Exception as e:
                    self.informacion_casassa['libro'] = None

                try: #BUSCAMOS AUTOR 
                    autor = soup.find('a', id='ContentPlaceHolderContenido_resultadosItems_rptResultados_rptAutores_0_a_autor_0')
                    autor_formateado = str(autor.text.strip("\n\t"))
                    self.informacion_casassa['autor'] = autor_formateado
                except Exception as e:
                    self.informacion_casassa['autor'] = None

                try: #BUSCAMOS PRECIO 
                    a_tag = soup.find('a', attrs={'data-precio': True})
                    if a_tag:
                        data_precio = a_tag['data-precio']
                        precio_soup = BeautifulSoup(data_precio, 'html.parser')
                        precio = precio_soup.get_text(strip=True).replace("$AR", "")
                        precio = precio.replace(".", "")
                        precio = precio.replace(",", ".")
                        self.informacion_casassa['precio'] = float(str(precio))
                    else:
                        self.informacion_casassa['precio'] = None
                except Exception as e:
                    self.informacion_casassa['precio'] = None

            else:
                print(f"Libro no encontrado en Casassa y Lorenzo: {response.url}")
                self.informacion_casassa = {'isbn': self.isbn, 'libro': None, 'autor': None ,'precio': None, 'libreria': 'Casassa y Lorenzo'}
            
            # print("Casassa: ",self.informacion_casassa)
            return self.informacion_casassa
        else:
            print(f"Error en la respuesta de la página Casassa y Lorenzo: {response.status_code}, {response.url}")
            self.informacion_casassa = {'isbn': self.isbn, 'libro': None, 'autor': None ,'precio': None, 'libreria': 'Casassa y Lorenzo'}


    def scrap_sbs(self, session):
        response = session.get(self.sbs_url)
        
        if response.status_code == 200:
            try:
                # Encuentra el script JSON en el HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                try:
                    script = soup.find('script', string=lambda text: text and text.startswith('{"Product:'))
                    if script:
                        data = json.loads(script.string)
                        # ENCUENTRA EL TITULO 
                        titulo = None
                        for key, value in data.items():
                            if isinstance(value, dict) and 'productName' in value:
                                titulo = value['productName']
                                break
                        if titulo:
                            titulo_formateado = titulo.upper()
                            self.informacion_sbs["libro"] = titulo_formateado

                            # ENCUENTRA EL AUTOR
                            autor = None
                            for key, value in data.items():
                                if isinstance(value, dict) and 'brand' in value:
                                    autor = value['brand']
                                    break
                            if autor:
                                autor_formateado = str(autor.upper())
                                self.informacion_sbs["autor"] = autor_formateado
                            else:
                                self.informacion_sbs["autor"] = None

                            # PRECIO
                            precio = self.find_price_sbs(data)
                            if precio:
                                precio_venta = float(precio[0][0])
                                precio_lista = float(precio[1][0])
                                # Al menor precio lo agrega al diccionario, si son iguales, agrega el precio de venta
                                if precio_venta < precio_lista:
                                    self.informacion_sbs["precio"] = precio_venta
                                else:
                                    self.informacion_sbs["precio"] = precio_lista
                            else:
                                self.informacion_sbs["precio"] = None
                        else:
                            self.informacion_sbs = {'isbn': self.isbn, 'libro': None, 'autor': None ,'precio': None, 'libreria': 'Sbs'}
                except Exception as e:
                    print("Error en el Script de Sbs: ", e)
                    self.informacion_sbs['autor'] = None

            except Exception as e:
                print(f"Error en la respuesta de la página Sbs: {e}, {response.url}")
                self.informacion_sbs = {'isbn': self.isbn, 'libro': None, 'autor': None ,'precio': None, 'libreria': 'Sbs'}

            # print("SBS: ", self.informacion_sbs)
            return self.informacion_sbs
        else:
            print(f"Error en la respuesta de la página Sbs: {response.status_code}, {response.url}")
            self.informacion_sbs = {'isbn': self.isbn, 'libro': None, 'autor': None ,'precio': None, 'libreria': 'Sbs'}

    def find_price_sbs(self, data):
        results = []
        if isinstance(data, dict):
            if "highPrice" in data and "lowPrice" in data:
                results.append((data["highPrice"], data["lowPrice"]))
            for key in data:
                results.extend(self.find_price_sbs(data[key]))
        elif isinstance(data, list):
            for item in data:
                results.extend(self.find_price_sbs(item))
        return results