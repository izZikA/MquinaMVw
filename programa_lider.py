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
        heartbeat_msg = b"Heartbeat"
        with master_lock:
            if master_node == (mi_ip, 5000):  # Verificar si este nodo es el maestro
                heartbeat_msg = b"Heartbeat:Master"

        for node in NODES:
            try:
                sock.sendto(heartbeat_msg, node)
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
    global master_node
    with master_lock:
        # Filtramos solo los nodos activos.
        active_nodes = [(node_ip, port) for node_ip, port in NODES if last_heartbeat.get((node_ip, port), 0) > time.time() - MAX_INACTIVE_TIME]
        
        # Si no hay nodos activos, no se puede elegir un maestro.
        if not active_nodes:
            print("No hay nodos activos para elegir un maestro.")
            master_node = None
            return
        
        # Seleccionar el nodo con la dirección IP más alta como maestro.
        new_master = max(active_nodes, key=lambda node: socket.inet_aton(node[0]))
        
        # Si hay un cambio en el nodo maestro, actualizar y mostrar mensaje.
        if new_master != master_node:
            master_node = new_master
            print(f"El nuevo nodo maestro es {master_node}")




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
            # Comprobar si la IP recibida corresponde a algún nodo en NODES.
            potential_new_master = (master_ip, 5000)
            if potential_new_master in NODES:
                global master_node
                # Si el maestro ha cambiado, actualizar y mostrar mensaje.
                if master_node != potential_new_master:
                    master_node = potential_new_master
                    print(f"El nuevo nodo maestro (recibido) es {master_node}")
            else:
                print(f"IP de maestro no reconocida: {master_ip}")


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
