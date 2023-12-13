import socket
import threading
import time

class Node:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.neighbors = []  # Lista de otros nodos (tuplas de host, puerto)

    def start_server(self):
        """ Inicia el servidor para escuchar heartbeats. """
        thread = threading.Thread(target=self.run_server)
        thread.start()

    def run_server(self):
        """ Maneja la lógica del servidor. """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()

            while True:
                conn, addr = s.accept()
                with conn:
                    print(f"Heartbeat recibido de {addr}")
                    # Aquí puedes añadir lógica para responder o procesar el heartbeat

    def send_heartbeat(self):
        """ Envía un heartbeat a todos los nodos vecinos. """
        for neighbor in self.neighbors:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect(neighbor)
                    s.sendall(b"Heartbeat")
                    print(f"Heartbeat enviado a {neighbor}")
                except ConnectionRefusedError:
                    print(f"No se pudo conectar a {neighbor}")

    def add_neighbor(self, neighbor):
        """ Añade un vecino a la lista. """
        self.neighbors.append(neighbor)
def main():
    # Crear nodos con sus respectivas direcciones IP
    node1 = Node('192.168.192.131', 65000)
    node2 = Node('192.168.192.130', 65000)
    node3 = Node('192.168.192.132', 65000)
    node4 = Node('192.168.192.133', 65000)

    # Añadir vecinos para cada nodo
    node1.add_neighbor(('192.168.192.130', 65000))
    node1.add_neighbor(('192.168.192.132', 65000))
    node1.add_neighbor(('192.168.192.133', 65000))

    node2.add_neighbor(('192.168.192.131', 65000))
    node2.add_neighbor(('192.168.192.132', 65000))
    node2.add_neighbor(('192.168.192.133', 65000))

    node3.add_neighbor(('192.168.192.131', 65000))
    node3.add_neighbor(('192.168.192.130', 65000))
    node3.add_neighbor(('192.168.192.133', 65000))

    node4.add_neighbor(('192.168.192.131', 65000))
    node4.add_neighbor(('192.168.192.130', 65000))
    node4.add_neighbor(('192.168.192.132', 65000))

    # Iniciar el servidor en cada nodo
    node1.start_server()
    node2.start_server()
    node3.start_server()
    node4.start_server()

    # Enviar heartbeats en un bucle
    while True:
        time.sleep(5)  # Intervalo de envío de heartbeat
        node1.send_heartbeat()
        node2.send_heartbeat()
        node3.send_heartbeat()
        node4.send_heartbeat()

if __name__ == "__main__":
    main()

