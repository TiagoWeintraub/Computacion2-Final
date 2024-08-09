from bs4 import BeautifulSoup
import json

class Libreria:
    def __init__(self, isbn):
        self.isbn = isbn
        self.informacion_cuspide = {'isbn': isbn, 'libro': '', 'autor': '' ,'precio': ''}
        self.informacion_casassa = {'isbn': isbn, 'libro': '', 'autor': '' ,'precio': ''}
        self.informacion_sbs = {'isbn': isbn, 'libro': '', 'autor': '' ,'precio': ''}
        
        # CORREGIR URLS, FALTA LA PARTE RESTANTE DE CASASSA Y SBS

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
                    self.informacion_cuspide['libro'] = "Libro no encontrado"

                try: # Autor 2
                    div_autor = soup.find('div', class_='product-info summary col-fit col entry-summary product-summary text-left form-minimal')
                    autor = div_autor.find('span', style='font-size: 14px;')
                    limpiando_autor = autor.text.strip()
                    self.informacion_cuspide['autor'] = limpiando_autor 

                except Exception as e:
                    self.informacion_cuspide['autor'] = "No encontrado"

                try: # Precio 3
                    precio = soup.find('p', class_='price product-page-price')
                    precio_formateado = str(precio.text.strip("\n$\xa0"))
                    precio_formateado = precio_formateado.replace(".", "")
                    precio_formateado = precio_formateado.replace(",", ".")
                    self.informacion_cuspide['precio'] = precio_formateado 
                except Exception as e:
                    self.informacion_cuspide['precio'] = "No encontrado"

            else:
                self.informacion_cuspide = {'isbn': self.isbn, 'libro': 'Libro no encontrado', 'autor': 'Autor no encontrado' ,'precio': 'Precio no encontrado'}
            
            print(self.informacion_cuspide)
            return self.informacion_cuspide
        else:
            print(f"Error en la respuesta de la página Cuspide: {response.status_code}")
            self.informacion_cuspide = {'isbn': self.isbn, 'libro': 'Libro no encontrado', 'autor': 'Autor no encontrado' ,'precio': 'Precio no encontrado'}


    def scrap_casassa(self, session):
        response = session.get(self.casassa_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            titulo = soup.find('a', id='ContentPlaceHolderContenido_rptFicha_a_titulo_0')
            print(titulo)
            if titulo:
                try: #BUSCAMOS TITULO 0
                    titulo_formateado = str(titulo.text.strip("\n\t"))
                    self.informacion_casassa['libro'] = titulo_formateado
                    print(titulo_formateado)
                except Exception as e:
                    self.informacion_casassa['libro'] = "Libro no encontrado"

                try: #BUSCAMOS AUTOR 1
                    autor = soup.find('a', id='ContentPlaceHolderContenido_rptFicha_rptAutores_0_a_autor_0')
                    autor_formateado = str(autor.text.strip("\n\t"))
                    self.informacion_casassa['autor'] = autor_formateado
                except Exception as e:
                    self.informacion_casassa['autor'] = "No aplica"

                try: #BUSCAMOS PRECIO 2
                    precio = soup.find('p', id='ContentPlaceHolderContenido_rptFicha_precioContainer_0')
                    precio_formateado = str(precio.text.strip(""))
                    precio_formateado = precio_formateado.replace("\xa0\xa0U$S", " |")
                    precio_formateado = precio_formateado.replace("\n\n\n$AR", "")
                    precio_formateado = precio_formateado.strip()
                    precio_formateado = precio_formateado.replace(".", "")
                    precio_formateado = precio_formateado.replace(",", ".")
                    lista_precio = precio_formateado.split()
                    self.informacion_casassa['precio'] = lista_precio[0]
                except Exception as e:
                    self.informacion_casassa['precio'] = "No aplica"

                else:
                    self.informacion_casassa = {'isbn': self.isbn, 'libro': 'Libro no encontrado', 'autor': 'Autor no encontrado' ,'precio': 'Precio no encontrado'}
                print(self.informacion_casassa)
            else:
                print(f"Error el scraping de casassa: {response.status_code}, {response.url}")
                self.informacion_casassa = {'isbn': self.isbn, 'libro': 'Libro no encontrado', 'autor': 'Autor no encontrado' ,'precio': 'Precio no encontrado'}
            
            print(self.informacion_casassa)
            return self.informacion_casassa
        else:
            print(f"Error en la respuesta de la página casassa: {response.status_code}, {response.url}")
            self.informacion_casassa = {'isbn': self.isbn, 'libro': 'Libro no encontrado', 'autor': 'Autor no encontrado' ,'precio': 'Precio no encontrado'}


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

    def scrap_sbs(self, session):
        response = session.get(self.sbs_url)

        if response.status_code == 200:
            try:
                # Encuentra el script JSON en el HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                script = soup.find('script', string=lambda text: text and text.startswith('{"Product:'))

                if script:
                    # Extrae el contenido del script y lo parsea como JSON
                    data = json.loads(script.string)
                    # ENCUENTRA EL TITULO 
                    titulo = None
                    for key, value in data.items():
                        if isinstance(value, dict) and 'productName' in value:
                            titulo = value['productName']
                            break
                    if titulo:
                        titulo_formateado = titulo.upper()
                        self.informacion_sbs['libro'] = titulo_formateado

                    # ENCUENTRA EL AUTOR 1
                        autor = None
                        for key, value in data.items():
                            if isinstance(value, dict) and 'brand' in value:
                                autor = value['brand']
                                break
                        if autor:
                            autor_formateado = str(autor.upper())
                            self.informacion_sbs['autor'] = autor_formateado
                        else:
                            self.informacion_sbs['autor'] = "Autor no encontrado"

                    # ENCUENTRA EL PRECIO (Venta y Lista) - Selecciona el menor de los dos
                        price = self.find_price_sbs(data)
                        if price: #Price es una lista de tuplas
                            precio_de_venta = price[0][0]
                            precio_de_lista = price[1][0]
                            #PRECIO DE VENTA 
                            if precio_de_venta!= 0 and precio_de_venta is not None:
                                precio_venta_int = int(precio_de_venta)
                            #PRECIO DE LISTA 
                            if precio_de_lista!= 0 and precio_de_lista is not None:
                                precio_lista_int = int(precio_de_lista)
                            if precio_venta_int and precio_lista_int:
                                # El menor de los dos precios se agrega a la lista, si son iguales se agrega cualquiera
                                if precio_venta_int < precio_lista_int:
                                    self.informacion_sbs['precio'] = precio_venta_int
                                else:
                                    self.informacion_sbs['precio'] = precio_lista_int
                            elif precio_de_venta == 0 or precio_de_venta is None:
                                self.informacion_sbs['precio'] = "Precio no encontrado"
                            elif precio_de_lista == 0 or precio_de_lista is None:
                                self.informacion_sbs['precio'] = "Precio no encontrado"
                            else:
                                self.informacion_sbs['precio'] = "Precio no encontrado"
                        else:
                            self.informacion_sbs['precio'] = "Precio no encontrado"

                    else:
                        self.informacion_sbs = {'isbn': self.isbn, 'libro': 'Libro no encontrado', 'autor': 'Autor no encontrado' ,'precio': 'Precio no encontrado'}
                else:
                    self.informacion_sbs = {'isbn': self.isbn, 'libro': 'Libro no encontrado', 'autor': 'Autor no encontrado' ,'precio': 'Precio no encontrado'}

            except Exception as e:
                print(f"Error en la respuesta de la página Sbs: {e}, {response.url}")
                self.informacion_sbs = {'isbn': self.isbn, 'libro': 'Libro no encontrado', 'autor': 'Autor no encontrado' ,'precio': 'Precio no encontrado'}
            else:
                print(f"Error en la respuesta de la página Sbs: {response.status_code}, {response.url}")
                self.informacion_sbs = {'isbn': self.isbn, 'libro': 'Libro no encontrado', 'autor': 'Autor no encontrado' ,'precio': 'Precio no encontrado'}

            print(self.informacion_sbs)
            return self.informacion_sbs
        else:
            print(f"Error en la respuesta de la página Sbs: {response.status_code}, {response.url}")
            self.informacion_sbs = {'isbn': self.isbn, 'libro': 'Libro no encontrado', 'autor': 'Autor no encontrado' ,'precio': 'Precio no encontrado'}

# print(Libreria(9789504988014).cuspide_url) # Asi se llama la url con el isbn