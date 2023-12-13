import socket
import threading
import time
import subprocess

# Direcciones IP y puertos de los nodos en la red
NODES = [("192.168.192.130", 5000), ("192.168.192.131", 5000),
         ("192.168.192.132", 5000), ("192.168.192.133", 5000)]

# Intervalo en segundos para enviar heartbeats
HEARTBEAT_INTERVAL = 5

# Tiempo máximo en segundos para considerar un nodo como inactivo
MAX_INACTIVE_TIME = 15

# Función para obtener la dirección IP de una interfaz
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

# Función para determinar el nodo maestro
def determinar_nodo_maestro():
    nodos_activos = [node for node, last_time in last_heartbeat.items() 
                     if time.time() - last_time <= MAX_INACTIVE_TIME]
    if nodos_activos:
        return max(nodos_activos, key=lambda node: node[0])
    return None

# Función que envía heartbeats a todos los nodos
def send_heartbeats():
    while True:
        maestro = determinar_nodo_maestro()
        es_maestro = (mi_ip, 5000) == maestro
        mensaje = b"Soy el maestro" if es_maestro else b"Heartbeat"

        for node in NODES:
            try:
                sock.sendto(mensaje, node)
            except Exception as e:
                print(f"Error al enviar heartbeat a {node}: {e}")
        time.sleep(HEARTBEAT_INTERVAL)

# Función que recibe heartbeats y actualiza el estado de los nodos
def receive_heartbeats():
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            last_heartbeat[addr] = time.time()
            es_maestro = data == b"Soy el maestro"
            if es_maestro:
                print(f"Heartbeat recibido de {addr}, es el nodo maestro")
            else:
                print(f"Heartbeat recibido de {addr}, nodo activo")
        except socket.timeout:
            pass

        # Verificar nodos inactivos
        verificar_nodos_inactivos()

def verificar_nodos_inactivos():
    current_time = time.time()
    for node in NODES:
        if current_time - last_heartbeat.get(node, 0) > MAX_INACTIVE_TIME:
            print(f"{node} ha dejado de estar activo")
            last_heartbeat[node] = current_time

# Obtener la dirección IP local
interfaz = "ens33"
mi_ip = obtener_direccion_ip(interfaz)

# Crear socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((mi_ip, 5000))
sock.settimeout(1)

# Registro de la última vez que se recibió un heartbeat de cada nodo
last_heartbeat = {node: 0 for node in NODES}

# Iniciar hilos para enviar y recibir heartbeats
send_thread = threading.Thread(target=send_heartbeats)
receive_thread = threading.Thread(target=receive_heartbeats)
send_thread.start()
receive_thread.start()
