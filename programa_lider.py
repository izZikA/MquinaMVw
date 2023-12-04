import socket
import threading
import time
import subprocess

# Direcciones IP y puertos de los nodos en la red
NODES = [("192.168.106.137", 5000), ("192.168.106.135", 5000)]
# Intervalo en segundos para enviar heartbeats
HEARTBEAT_INTERVAL = 5
# Tiempo máximo en segundos para considerar un nodo como inactivo
MAX_INACTIVE_TIME = 15

# Registro de la última vez que se recibió un heartbeat de cada nodo
last_heartbeat = {}

# Nodo maestro actual
nodo_maestro = None

# Esta función elige el nodo con la IP más alta como maestro
def elegir_nodo_maestro(nodos):
    return max(nodos, key=lambda node: socket.inet_aton(node[0]))

# Esta función envía heartbeats a todos los nodos
def send_heartbeats():
    global nodo_maestro
    while True:
        for node in NODES:
            try:
                # Incluir información del nodo maestro en el mensaje
                msg = f"Heartbeat from {mi_ip}, master: {nodo_maestro[0]}"
                sock.sendto(msg.encode(), node)
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

        # Verificar el estado del nodo maestro
        verificar_nodo_maestro()

def verificar_nodo_maestro():
    global nodo_maestro
    current_time = time.time()
    if nodo_maestro and current_time - last_heartbeat.get(nodo_maestro, 0) > MAX_INACTIVE_TIME:
        print(f"El nodo maestro {nodo_maestro} ha dejado de estar activo. Reelecting master node.")
        nodo_maestro = elegir_nodo_maestro([node for node in NODES if node != nodo_maestro])
        print(f"Nuevo nodo maestro es {nodo_maestro}")

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

# Asignar el nodo maestro inicial
nodo_maestro = elegir_nodo_maestro(NODES)

# Crear socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((mi_ip, 5000))
sock.settimeout(1)

# Iniciar hilos para enviar y recibir heartbeats
send_thread = threading.Thread(target=send_heartbeats)
receive_thread = threading.Thread(target=receive_heartbeats)
send_thread.start()
receive_thread.start()

send_thread.join()
receive_thread.join()
