import socket

class Cliente:
    def __init__(self, host='localhost', port=5005):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def conectar(self):
        try:
            self.client_socket.connect((self.host, self.port))
            print(f"""\n_________________________________________________________________\n\n._________________ ¡Bienvenido a BEST SEARCH! __________________.\n:::::....... Conectado al servidor en {self.host}:{self.port} .......:::::\n_________________________________________________________________\n
                """)
        except Exception as e:
            print(f"No se pudo conectar al servidor: {e}")
            self.cerrar_conexion()

    def enviar_isbn(self, isbn):
        try:
            self.client_socket.send(isbn.encode())
            print(f"\n Código ISBN enviado: {isbn}")

            response = self.client_socket.recv(1024).decode()
            print(f"Respuesta del servidor: {response}")
        except Exception as e:
            print(f"Error al enviar ISBN o recibir respuesta: {e}")

    def cerrar_conexion(self):
        self.client_socket.close()
        print("\nConexión cerrada\n")

if __name__ == "__main__":
    cliente = Cliente()
    cliente.conectar()

    while True:
        isbn = input("\n|---> Introduce el código ISBN13 del libro ('Q' para salir): ")

        # Validación del ISBN o 'q' para salir
        if len(isbn) != 13 and isbn.lower() != 'q':
            print("\nError | El ISBN ingresado no tiene 13 dígitos o ingresó un caracter no válido, intente de nuevo.")
            continue

        # Si el usuario escribe 'q', se cierra la conexión y termina el programa
        if isbn.lower() == 'q':
            cliente.cerrar_conexion()
            break

        # Enviar el ISBN al servidor
        cliente.enviar_isbn(isbn)

