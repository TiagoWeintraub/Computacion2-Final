import socket

class Cliente:
    def __init__(self, host='localhost', port=5005):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conexion = False

    def conectar(self):
        try:
            self.conexion = True
            self.client_socket.connect((self.host, self.port))
            cliente = self.client_socket.recv(1024).decode()
            print(f"""\n______________________ ¡Bienvenido a BEST SEARCH! ________________________\n\n :::.... {cliente} ya está conectado al servidor en {self.host}:{self.port} ....:::\n\n    Web Scraping en librerías: Cúspide - Casassa y Lorenzo - Sbs\n__________________________________________________________________________""")
        except Exception as e:
            print(f"No se pudo conectar al servidor: {e}")
            self.cerrar_conexion()
            self.conexion = False

    def enviar_isbn(self, isbn):
        try:
            self.client_socket.send(isbn.encode())
            print(f"\n Código ISBN enviado: {isbn}")

            response = self.client_socket.recv(1024).decode()
            print(response)
        except Exception as e:
            print(f"Error al enviar ISBN o recibir respuesta: {e}")

    def cerrar_conexion(self):
        self.enviar_isbn("q")
        self.client_socket.close()
        print("\nConexión cerrada\n")

if __name__ == "__main__":
    cliente = Cliente()
    cliente.conectar()

    while cliente.conexion:
        isbn = input("\n|---> Introduce el código ISBN13 del libro ('Q' para salir): ")

        if len(isbn) != 13 and isbn.lower() != 'q': # Validación del ISBN o 'q' para salir
            print("\nError | El ISBN ingresado no tiene 13 dígitos o ingresó un caracter no válido, intente de nuevo.")
            continue
        if isbn.lower() == 'q':
            cliente.cerrar_conexion()
            break

        cliente.enviar_isbn(isbn) # Enviar el ISBN al servidor

