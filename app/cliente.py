import socket

class Cliente:
    def __init__(self, host_ipv4='127.0.0.1', host_ipv6='::1', port=5005):
        self.host_ipv4 = host_ipv4
        self.host_ipv6 = host_ipv6
        self.port = port
        self.client_socket = None
        self.conexion = False

    def configurar_conexion(self):
        tipo_conexion = input("¿Desea usar IPv4 o IPv6? (4/6): ").strip()
        if tipo_conexion == '4':
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.host = self.host_ipv4
        elif tipo_conexion == '6':
            self.client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            self.host = self.host_ipv6
        else:
            print("Opción no válida. Por favor, elija '4' para IPv4 o '6' para IPv6.")
            return False
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
