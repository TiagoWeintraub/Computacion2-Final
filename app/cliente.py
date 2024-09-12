import socket
import os


class Cliente:
    def __init__(self):
        self.port = int(os.getenv("PUERTO", 5555)) 
        self.client_socket = None
        self.conexion = False

    def obtener_direccion_ipv6(self):
        try:
            hostname = socket.gethostname()
            direccion_ipv6 = socket.getaddrinfo(hostname, None, socket.AF_INET6)[0][4][0]
            return direccion_ipv6
        except Exception as e:
            print(f"No se pudo obtener la dirección IPv6: {e}")
            return False

    def obtener_direccion_ipv4(self):
        try:
            hostname = socket.gethostname()
            direccion_ipv4 = socket.gethostbyname(hostname)
            return direccion_ipv4
        except Exception as e:
            print(f"No se pudo obtener la dirección IPv4: {e}")
            return None

    def configurar_conexion(self):
        direccion_ip = self.obtener_direccion_ipv6() # Intenta obtener la IPv6
        print(f"\nDirección IP obtenida: {direccion_ip}")
        
        if direccion_ip is False: # Si no se pudo obtener la IPv6, se obtiene la IPv4
            print("No se pudo obtener una dirección IP válida.")
            direccion_ip = self.obtener_direccion_ipv4()
        # Determina si es IPv6 o IPv4
        if ':' in direccion_ip:
            self.client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.host = direccion_ip
        return True

    def conectar(self):
        if not self.configurar_conexion():
            return

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
        self.client_socket.close()
        print("\nConexión cerrada\n")

if __name__ == "__main__":
    PUERTO = int(os.getenv("PUERTO"))
    cliente = Cliente()
    print(cliente.port)
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