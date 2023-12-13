import socket
import threading
import time
import subprocess
import random
from functools import cmp_to_key

# Direcciones IP y puertos de los nodos en la red
NODES = [("192.168.192.130", 5000), ("192.168.192.131", 5000), ("192.168.192.132", 5000), ("192.168.192.133", 5000)]
# Intervalo en segundos para enviar heartbeats
HEARTBEAT_INTERVAL = 5
# Tiempo máximo en segundos para considerar un nodo como inactivo
MAX_INACTIVE_TIME = 15

# Variable global para almacenar la IP del nodo maestro
master_node = None
# Lock para manejar el acceso concurrente a la variable master_node
master_lock = threading.Lock()

# Registro de la última vez que se recibió un heartbeat de cada nodo
last_heartbeat = {}

def send_heartbeats():
    while True:
        for node in NODES:
            try:
                sock.sendto(b"Heartbeat", node)
            except Exception as e:
                print(f"Error al enviar heartbeat a {node}: {e}")
        time.sleep(HEARTBEAT_INTERVAL)

def receive_heartbeats():
    global master_node
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            last_heartbeat[addr] = time.time()
            print(f"Heartbeat recibido de {addr}, nodo activo")
            update_master_status(data, addr)
        except socket.timeout:
            pass

        current_time = time.time()
        for node in NODES:
            if current_time - last_heartbeat.get(node, 0) > MAX_INACTIVE_TIME:
                print(f"{node} ha dejado de estar activo")
                last_heartbeat[node] = current_time

        with master_lock:
            if master_node and (master_node not in last_heartbeat or current_time - last_heartbeat[master_node] > MAX_INACTIVE_TIME):
                print(f"Nodo maestro {master_node} ha dejado de estar activo. Iniciando nueva elección.")
                master_node = None
                time.sleep(random.uniform(0.5, 1.5))  # Retraso aleatorio para evitar condiciones de carrera
                choose_master()

def choose_master():
    with master_lock:
        active_nodes = [node for node in NODES if last_heartbeat.get(node, 0) > time.time() - MAX_INACTIVE_TIME]
        if active_nodes:
            global master_node
            master_node = max(active_nodes, key=lambda node: socket.inet_aton(node[0]))
            print(f"El nodo maestro es {master_node}")

def broadcast_master_status():
    while True:
        with master_lock:
            if master_node:
                for node in NODES:
                    try:
                        sock.sendto(f"Master:{master_node[0]}".encode(), node)
                    except Exception as e:
                        print(f"Error al enviar estado del maestro a {node}: {e}")
        time.sleep(HEARTBEAT_INTERVAL)

def update_master_status(data, addr):
    if data.startswith(b"Master:"):
        with master_lock:
            _, master_ip = data.decode().split(":")
            global master_node
            master_node = (master_ip, 5000)

def obtener_direccion_ip(interface):
    try:
        resultado = subprocess.check_output(['ip', 'addr', 'show', interface]).decode('utf-8')
        for linea in resultado.split('\n'):
            if 'inet' in linea:
                partes = linea.strip().split()
                inet_index = partes.index('inet')
                direccion_ip = partes[inet_index + 1].split('/')[0]
                return direccion_ip
    except subprocess.CalledProcessError:
        return "No se pudo obtener la dirección IP"

interfaz = "ens33"
mi_ip = obtener_direccion_ip(interfaz)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((mi_ip, 5000))
sock.settimeout(1)

send_thread = threading.Thread(target=send_heartbeats)
receive_thread = threading.Thread(target=receive_heartbeats)
master_broadcast_thread = threading.Thread(target=broadcast_master_status)

send_thread.start()
receive_thread.start()
master_broadcast_thread.start()

send_thread.join()
receive_thread.join()
master_broadcast_thread.join()
