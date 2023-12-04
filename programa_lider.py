import socket
import threading
import time
import subprocess


# Direcciones IP y puertos de los nodos en la red
NODES = [("192.168.192.", 5000), ("192.168.192.", 5000)]
# Intervalo en segundos para enviar heartbeats
HEARTBEAT_INTERVAL = 5
# Tiempo máximo en segundos para considerar un nodo como inactivo
MAX_INACTIVE_TIME = 15

# Esta función envía heartbeats a todos los nodos
def send_heartbeats():
    while True:
        for node in NODES:
            try:
                sock.sendto(b"Heartbeat", node)
            except Exception as e:
                print(f"Error al enviar heartbeat a {node}: {e}")
        time.sleep(HEARTBEAT_INTERVAL)

# Esta función recibe heartbeats y actualiza el estado de los nodos
def receive_heartbeats():
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            last_heartbeat[addr] = time.time()
            print(f"Heartbeat recibido de {addr}, nodo activo")
        except socket.timeout:
            pass

        # Verificar nodos inactivos
        current_time = time.time()
        for node in NODES:
            if current_time - last_heartbeat.get(node, 0) > MAX_INACTIVE_TIME:
                print(f"{node} ha dejado de estar activo")
                last_heartbeat[node] = current_time


def obtener_direccion_ip(interface):
    try:
        # Ejecutar el comando 'ip addr' y capturar la salida
        resultado = subprocess.check_output(['ip', 'addr', 'show', interface]).decode('utf-8')

        # Buscar la línea que contiene 'inet' en la salida del comando
        for linea in resultado.split('\n'):
            if 'inet' in linea:
                partes = linea.strip().split()
                inet_index = partes.index('inet')
                direccion_ip = partes[inet_index + 1].split('/')[0]
                return direccion_ip

    except subprocess.CalledProcessError:
        return "No se pudo obtener la dirección IP"
    

interfaz = "ens33"
mi_ip=obtener_direccion_ip(interfaz)

# Crear socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Asignar IP y puerto local
sock.bind((mi_ip, 5000))
sock.settimeout(1)

# Registro de la última vez que se recibió un heartbeat de cada nodo
last_heartbeat = {}

# Iniciar hilos para enviar y recibir heartbeats
send_thread = threading.Thread(target=send_heartbeats)
receive_thread = threading.Thread(target=receive_heartbeats)
send_thread.start()
receive_thread.start()

send_thread.join()
receive_thread.join()

