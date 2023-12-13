import socket
import threading
import time
import subprocess

# Configuraciones iniciales
NODES = [("192.168.192.131", 5000), ("192.168.192.130", 5000), ("192.168.192.132", 5000), ("192.168.192.133", 5000)]
HEARTBEAT_INTERVAL = 5
MAX_INACTIVE_TIME = 15

# Variables globales
maestro_actual = None
soy_el_maestro = False
master_lock = threading.Lock()  # Lock para controlar el acceso a la variable maestro_actual
last_heartbeat = {}


# Función para obtener la dirección IP del nodo actual
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

# Función para enviar heartbeats a todos los nodos
def send_heartbeats():
    while True:
        msg = f"Heartbeat from {mi_ip}"
        if soy_el_maestro:
            msg += " | soy el nodo maestro"
        for node in NODES:
            try:
                sock.sendto(msg.encode(), node)
            except Exception as e:
                print(f"Error al enviar heartbeat a {node}: {e}")
        time.sleep(HEARTBEAT_INTERVAL)

# Función para recibir heartbeats y actualizar el estado de los nodos
def receive_heartbeats():
    global maestro_actual, soy_el_maestro
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            mensaje = data.decode()
            last_heartbeat[addr] = time.time()

            with master_lock:
                if "soy el nodo maestro" in mensaje:
                    if not maestro_actual or addr[0] > maestro_actual:
                        actualizar_estado_maestro(addr[0])
                else:
                    # Si recibimos un heartbeat normal, y no hay maestro, se considera ser maestro
                    if not maestro_actual and deberia_ser_maestro():
                        declarar_como_maestro()
        except socket.timeout:
            pass
        verificar_nodos_inactivos()


def deberia_ser_maestro():
    global mi_ip, last_heartbeat
    # Se considera ser maestro si tiene la IP más alta entre todos los nodos conocidos
    for node in NODES:
        if node[0] != mi_ip and last_heartbeat.get(node, 0) + MAX_INACTIVE_TIME > time.time():
            if node[0] > mi_ip:
                return False
    return True


# Actualizar el estado del nodo maestro
def actualizar_estado_maestro(ip_maestro):
    global maestro_actual
    maestro_actual = ip_maestro

# Declarar este nodo como maestro
def declarar_como_maestro():
    global soy_el_maestro
    soy_el_maestro = True
    print(f"{mi_ip} se ha declarado como el nodo maestro")

# Verificar si hay un maestro activo
def hay_maestro_activo():
    global maestro_actual
    return maestro_actual and (time.time() - last_heartbeat.get((maestro_actual, 5000), 0)) < MAX_INACTIVE_TIME

# Verificar nodos inactivos
def verificar_nodos_inactivos():
    global maestro_actual
    current_time = time.time()
    for node in NODES:
        if current_time - last_heartbeat.get(node, 0) > MAX_INACTIVE_TIME:
            if node[0] == maestro_actual:
                print(f"El nodo maestro {node} ha dejado de estar activo")
                maestro_actual = None
                soy_el_maestro = False
            print(f"{node} ha dejado de estar activo")

# Configuración inicial del nodo
interfaz = "ens33"
mi_ip = obtener_direccion_ip(interfaz)

# Creación y configuración del socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((mi_ip, 5000))
sock.settimeout(1)

# Iniciar hilos para enviar y recibir heartbeats
send_thread = threading.Thread(target=send_heartbeats)
receive_thread = threading.Thread(target=receive_heartbeats)
send_thread.start()
receive_thread.start()

# Los hilos se unen al hilo principal para mantenerse ejecutando
send_thread.join()
receive_thread.join()

