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
                    self.informacion_cuspide['precio'] = float(str(precio_formateado))
                except Exception as e:
                    self.informacion_cuspide['precio'] = "No encontrado"

            else:
                self.informacion_cuspide = {'isbn': self.isbn, 'libro': 'Libro no encontrado', 'autor': 'Autor no encontrado' ,'precio': 'Precio no encontrado'}
            
            print("Cuspide: ", self.informacion_cuspide)
            return self.informacion_cuspide
        else:
            print(f"Error en la respuesta de la página Cuspide: {response.status_code}")
            self.informacion_cuspide = {'isbn': self.isbn, 'libro': 'Libro no encontrado', 'autor': 'Autor no encontrado' ,'precio': 'Precio no encontrado'}

    def scrap_casassa(self, session):
        response = session.get(self.casassa_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            titulo = soup.find('a', id='ContentPlaceHolderContenido_resultadosItems_rptResultados_a_titulo_0')
            if titulo:
                try: #BUSCAMOS TITULO 0
                    titulo_formateado = str(titulo.text.strip("\n\t"))
                    self.informacion_casassa['libro'] = titulo_formateado
                except Exception as e:
                    self.informacion_casassa['libro'] = "Libro no encontrado"

                try: #BUSCAMOS AUTOR 1
                    autor = soup.find('a', id='ContentPlaceHolderContenido_resultadosItems_rptResultados_rptAutores_0_a_autor_0')
                    autor_formateado = str(autor.text.strip("\n\t"))
                    self.informacion_casassa['autor'] = autor_formateado
                except Exception as e:
                    self.informacion_casassa['autor'] = "Autor no encontrado"

                try: #BUSCAMOS PRECIO 2
                    a_tag = soup.find('a', attrs={'data-precio': True})
                    if a_tag:
                        # Obtener el valor del atributo data-precio
                        data_precio = a_tag['data-precio']

                        # Parsear el contenido de data-precio como HTML
                        precio_soup = BeautifulSoup(data_precio, 'html.parser')

                        # Extraer el texto dentro de data-precio
                        precio = precio_soup.get_text(strip=True).replace("$AR", "")
                        precio = precio.replace(".", "")
                        precio = precio.replace(",", ".")
                        self.informacion_casassa['precio'] = float(str(precio))
                    else:
                        self.informacion_casassa['precio'] = "Precio no encontrado"
                except Exception as e:
                    self.informacion_casassa['precio'] = "Precio no encontrado"

            else:
                print(f"Error el scraping de casassa: {response.status_code}, {response.url}")
                print(f"No entra en el if porque no encuentra el titulo, el titulo es {titulo}")
                self.informacion_casassa = {'isbn': self.isbn, 'libro': 'Libro no encontrado', 'autor': 'Autor no encontrado' ,'precio': 'Precio no encontrado'}
            
            print("Casassa: ",self.informacion_casassa)
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

                # ENCUENTRA EL TITULO 
                titulo = soup.find('span', class_='vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-productBrand--nombreVitrina vtex-product-summary-2-x-brandName vtex-product-summary-2-x-brandName--nombreVitrina t-body')
                print("Titulo: ", titulo)
                
                spans = soup.find_all('span', class_='vtex-product-price-1-x-currencyInteger vtex-product-price-1-x-currencyInteger--precioVitrina')


                # ENCUENTRA EL AUTOR --------------------- FALTA ESTO Y PONER LOS TRY EXCEPT
                
                # PRECIO
                lista_precios = []
                for span in spans:
                    precio = span.get_text(strip=True)
                    print(f"Precio encontrado: {precio}")
                    lista_precios.append(precio)
                
                precio = ""
                print("Lista de precios: ", lista_precios)
                # concatenar los precios
                for i in range(len(lista_precios)):
                    precio += lista_precios[i]
                print("Precio concatenado: ", float(precio))
                
                





            except Exception as e:
                print(f"Error en la respuesta de la página Sbs: {e}, {response.url}")
                self.informacion_sbs = {'isbn': self.isbn, 'libro': 'Libro no encontrado', 'autor': 'Autor no encontrado' ,'precio': 'Precio no encontrado'}
        else:
            print(f"Error en la respuesta de la página Sbs: {response.status_code}, {response.url}")
            self.informacion_sbs = {'isbn': self.isbn, 'libro': 'Libro no encontrado', 'autor': 'Autor no encontrado' ,'precio': 'Precio no encontrado'}


    # def scrap_sbs(self, session):
    #     response = session.get(self.sbs_url)

    #     if response.status_code == 200:
    #         try:
    #             # Encuentra el script JSON en el HTML
    #             soup = BeautifulSoup(response.content, 'html.parser')
    #             # Crea un archivo txt con el contenido de la página
    #             with open('sbs.html', 'w') as file:
    #                 file.write(soup.prettify())
    #             script = soup.find('script', string=lambda text: text and text.startswith('{"Product:'))

    #             if script:
    #                 # Extrae el contenido del script y lo parsea como JSON
    #                 data = json.loads(script.string)
    #                 # ENCUENTRA EL TITULO 
    #                 titulo = None
    #                 for key, value in data.items():
    #                     if isinstance(value, dict) and 'productName' in value:
    #                         titulo = value['productName']
    #                         break
    #                 if titulo:
    #                     titulo_formateado = titulo.upper()
    #                     self.informacion_sbs['libro'] = titulo_formateado

    #                 # ENCUENTRA EL AUTOR 1
    #                     autor = None
    #                     for key, value in data.items():
    #                         if isinstance(value, dict) and 'brand' in value:
    #                             autor = value['brand']
    #                             break
    #                     if autor:
    #                         autor_formateado = str(autor.upper())
    #                         self.informacion_sbs['autor'] = autor_formateado
    #                     else:
    #                         self.informacion_sbs['autor'] = "Autor no encontrado"

    #                 # ENCUENTRA EL PRECIO (Venta y Lista) - Selecciona el menor de los dos
    #                     price = self.find_price_sbs(data)
    #                     if price: #Price es una lista de tuplas
    #                         precio_de_venta = price[0][0]
    #                         precio_de_lista = price[1][0]
    #                         #PRECIO DE VENTA 
    #                         if precio_de_venta!= 0 and precio_de_venta is not None:
    #                             precio_venta_int = int(precio_de_venta)
    #                         #PRECIO DE LISTA 
    #                         if precio_de_lista!= 0 and precio_de_lista is not None:
    #                             precio_lista_int = int(precio_de_lista)
    #                         if precio_venta_int and precio_lista_int:
    #                             # El menor de los dos precios se agrega a la lista, si son iguales se agrega cualquiera
    #                             if precio_venta_int < precio_lista_int:
    #                                 self.informacion_sbs['precio'] = precio_venta_int
    #                             else:
    #                                 self.informacion_sbs['precio'] = precio_lista_int
    #                         elif precio_de_venta == 0 or precio_de_venta is None:
    #                             self.informacion_sbs['precio'] = "Precio no encontrado"
    #                         elif precio_de_lista == 0 or precio_de_lista is None:
    #                             self.informacion_sbs['precio'] = "Precio no encontrado"
    #                         else:
    #                             self.informacion_sbs['precio'] = "Precio no encontrado"
    #                     else:
    #                         self.informacion_sbs['precio'] = "Precio no encontrado"

    #                 else:
    #                     self.informacion_sbs = {'isbn': self.isbn, 'libro': 'Libro no encontrado', 'autor': 'Autor no encontrado' ,'precio': 'Precio no encontrado'}
    #             else:
    #                 self.informacion_sbs = {'isbn': self.isbn, 'libro': 'Libro no encontrado', 'autor': 'Autor no encontrado' ,'precio': 'Precio no encontrado'}

    #         except Exception as e:
    #             print(f"Error en la respuesta de la página Sbs: {e}, {response.url}")
    #             self.informacion_sbs = {'isbn': self.isbn, 'libro': 'Libro no encontrado', 'autor': 'Autor no encontrado' ,'precio': 'Precio no encontrado'}
    #         else:
    #             print(f"Error en la respuesta de la página Sbs: {response.status_code}, {response.url}")
    #             self.informacion_sbs = {'isbn': self.isbn, 'libro': 'Libro no encontrado', 'autor': 'Autor no encontrado' ,'precio': 'Precio no encontrado'}

    #         print(self.informacion_sbs)
    #         return self.informacion_sbs
    #     else:
    #         print(f"Error en la respuesta de la página Sbs: {response.status_code}, {response.url}")
    #         self.informacion_sbs = {'isbn': self.isbn, 'libro': 'Libro no encontrado', 'autor': 'Autor no encontrado' ,'precio': 'Precio no encontrado'}

# print(Libreria(9789504988014).cuspide_url) # Asi se llama la url con el isbn