import socket

class Cliente:
    def __init__(self, host='localhost', port=5005):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def conectar(self):
        try:
            self.client_socket.connect((self.host, self.port))
            print(f"Conectado al servidor en {self.host}:{self.port}")
        except Exception as e:
            print(f"No se pudo conectar al servidor: {e}")

    def enviar_isbn(self, isbn):
        try:
            self.client_socket.send(isbn.encode())
            print(f"ISBN enviado: {isbn}")

            response = self.client_socket.recv(1024).decode()
            print(f"Respuesta del servidor: {response}")
        except Exception as e:
            print(f"Error al enviar ISBN o recibir respuesta: {e}")
        finally:
            self.client_socket.close()

if __name__ == "__main__":
    cliente = Cliente()  # Asegúrate de que el host y puerto coincidan con los del servidor
    cliente.conectar()

    isbn = input("Introduce el ISBN13 del libro: ")
    cliente.enviar_isbn(isbn)
