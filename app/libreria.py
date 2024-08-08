from bs4 import BeautifulSoup

class Libreria:
    def __init__(self, isbn):
        self.isbn = isbn
        self.informacion_cuspide = {'isbn': isbn, 'libro': '', 'autor': '' ,'precio': ''}
        self.informacion_casassa = {'isbn': isbn, 'libro': '', 'autor': '' ,'precio': ''}
        self.informacion_sbs = {'isbn': isbn, 'libro': '', 'autor': '' ,'precio': ''}

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
        else:
            print(f"Error en la respuesta de la página Cuspide: {response.status_code}")
            self.informacion_cuspide = {'isbn': self.isbn, 'libro': 'Libro no encontrado', 'autor': 'Autor no encontrado' ,'precio': 'Precio no encontrado'}

    def scrap_casassa(self, session):
        pass
    
    def scrap_sbs(self, session):
        pass

# print(Libreria(9789504988014).cuspide_url) # Asi se llama la url con el isbn


