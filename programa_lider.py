import socket
import threading
import time
import subprocess

# Direcciones IP y puertos de los nodos en la red
NODES = [("192.168.106.135", 5000), ("192.168.106.137", 5000),
         ("192.168.106.138", 5000)]
# Intervalo en segundos para enviar heartbeats
HEARTBEAT_INTERVAL = 5
# Tiempo máximo en segundos para considerar un nodo como inactivo
MAX_INACTIVE_TIME = 15

# Esta función envía heartbeats a todos los nodos
def send_heartbeats():
    global master_node
    while True:
        heartbeat_msg = "Heartbeat"
        with master_lock:
            if (mi_ip, 5000) == master_node:
                heartbeat_msg += ":Master"
        for node in NODES:
            try:
                sock.sendto(heartbeat_msg.encode(), node)
            except Exception as e:
                print(f"Error al enviar heartbeat a {node}: {e}")
        time.sleep(HEARTBEAT_INTERVAL)

# Esta función recibe heartbeats y actualiza el estado de los nodos
def receive_heartbeats_modified():
    global master_node
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            last_heartbeat[addr] = time.time()
            if "Master" in data.decode():
                with master_lock:
                    if addr != master_node:
                        print(f"Nuevo nodo maestro elegido: {addr}")
                        master_node = addr
            print(f"Heartbeat recibido de {addr}, nodo activo")
        except socket.timeout:
            pass

        # Verificar nodos inactivos y actualizar el nodo maestro
        determine_master()

# Función para determinar el nodo maestro
def determine_master():
    global master_node
    with master_lock:
        active_nodes = {node: last_heartbeat[node] for node in NODES if time.time() - last_heartbeat.get(node, 0) <= MAX_INACTIVE_TIME}
        if active_nodes:
            highest_ip = max(active_nodes.keys())
            if highest_ip != master_node:
                master_node = highest_ip
                print(f"El nodo maestro actual es: {master_node}")

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

# Obtener dirección IP de la interfaz
interfaz = "ens33"
mi_ip = obtener_direccion_ip(interfaz)

# Crear socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Asignar IP y puerto local
sock.bind((mi_ip, 5000))
sock.settimeout(1)

# Registro de la última vez que se recibió un heartbeat de cada nodo
last_heartbeat = {}

# Lock para control de acceso concurrente al nodo maestro
master_lock = threading.Lock()

# Nodo maestro actual
master_node = None

# Iniciar hilos para enviar y recibir heartbeats
send_thread = threading.Thread(target=send_heartbeats)
receive_thread = threading.Thread(target=receive_heartbeats_modified)
send_thread.start()
receive_thread.start()

send_thread.join()
receive_thread.join()
