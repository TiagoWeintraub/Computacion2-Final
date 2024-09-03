import socket

class Cliente:
    def __init__(self, host='127.0.0.1', host_ipv6='::1', port=5555):
        self.host = host
        self.host_ipv6 = host_ipv6
        self.port = port
        self.client_socket = None
        self.conexion = False

    def configurar_conexion(self):
        tipo_conexion = input("\n¿Desea usar IPv4 o IPv6? Ingrese 4, 6 o 'Q' para salir: ").strip() #Backslash para escapar el caracter especial en la cadena de texto: '4/6' -> '4\/6'
        while tipo_conexion not in ['4', '6', 'q', 'Q']:
            tipo_conexion = input("\nOpción no válida. | Por favor, elija '4' para IPv4 - '6' para IPv6 ('Q' para salir): ").strip()

        if tipo_conexion == '4':
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.host = self.host
                self.port = self.port
            except Exception as e:
                print(f"Error al crear el socket IPv4: {e}")
                return False
        elif tipo_conexion == '6': # Configuración de la conexión IPv6
            try:
                self.client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                self.host = self.host_ipv6
                self.port = self.port
            except Exception as e:
                print(f"Error al crear el socket IPv6: {e}")
                return False
        elif tipo_conexion in ['q', 'Q']:
            return False
            
        else:
            print("Opción no válida. | Por favor, elija '4' para IPv4 o '6' para IPv6.")
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
