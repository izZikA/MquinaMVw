import socket
import threading
import time
import subprocess

# Direcciones IP y puertos de los nodos en la red
NODES = [("192.168.192.13", 5000), ("192.168.192.13", 5000)]
# Ordenar los nodos por dirección IP de mayor a menor
NODES.sort(key=lambda node: node[0], reverse=True)

# Intervalo en segundos para enviar heartbeats
HEARTBEAT_INTERVAL = 5
# Tiempo máximo en segundos para considerar un nodo como inactivo
MAX_INACTIVE_TIME = 15

# El nodo maestro inicial es el de la IP más alta
master_node = NODES[0]

# Esta función envía heartbeats a todos los nodos
def send_heartbeats():
    while True:
        for node in NODES:
            try:
                # El mensaje incluye la IP del nodo maestro
                msg = f"Heartbeat from {mi_ip}, master is {master_node[0]}"
                sock.sendto(msg.encode(), node)
            except Exception as e:
                print(f"Error al enviar heartbeat a {node}: {e}")
        time.sleep(HEARTBEAT_INTERVAL)

# Esta función recibe heartbeats y actualiza el estado de los nodos
def receive_heartbeats():
    global master_node
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            message = data.decode()
            source_ip = addr[0]
            last_heartbeat[addr] = time.time()
            print(f"{message}, nodo activo")

            # Si el nodo maestro actual deja de estar activo, elegir uno nuevo
            if master_node[0] == source_ip and 'master is' in message:
                master_ip = message.split('master is ')[1]
                if master_node[0] != master_ip:
                    master_node = (master_ip, master_node[1])
                    print(f"Nuevo nodo maestro es {master_node[0]}")

        except socket.timeout:
            pass

        # Verificar nodos inactivos y reelección de maestro si es necesario
        check_inactive_nodes()

def check_inactive_nodes():
    global master_node
    current_time = time.time()
    inactive_nodes = [node for node in NODES if current_time - last_heartbeat.get(node, 0) > MAX_INACTIVE_TIME]

    for node in inactive_nodes:
        print(f"{node} ha dejado de estar activo")

        # Si el nodo maestro está inactivo, se debe elegir uno nuevo
        if node == master_node:
            print("El nodo maestro ha dejado de estar activo. Se está eligiendo uno nuevo...")
            # Elegir el nodo con la IP más alta que siga activo
            active_nodes = [n for n in NODES if n not in inactive_nodes]
            if active_nodes:
                master_node = active_nodes[0]
                print(f"El nuevo nodo maestro es {master_node[0]}")
            else:
                print("No hay nodos activos disponibles para ser maestro.")

        # Actualizar el tiempo para evitar múltiples impresiones
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
mi_ip = obtener_direccion_ip(interfaz)

# Crear socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Asignar IP y puerto local
sock.bind((mi_ip, 5000))
sock.settimeout(1)

# Registro de la última vez que se recibió un heartbeat de cada nodo
last_heartbeat = {node: 0 for node in NODES}

# Iniciar hilos para enviar y recibir heartbeats
send_thread = threading.Thread(target=send_heartbeats)
receive_thread = threading.Thread(target=receive_heartbeats)
send_thread.start()
receive_thread.start()

send_thread.join()
receive_thread.join()

