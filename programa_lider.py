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
master_lock = threading.Lock()
last_heartbeat = {}
mi_ip = None  # Se definirá después

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
    global soy_el_maestro
    next_heartbeat_time = time.time() + HEARTBEAT_INTERVAL
    while True:
        current_time = time.time()
        if current_time >= next_heartbeat_time:
            msg = f"Heartbeat from {mi_ip}"
            if soy_el_maestro:
                msg += " | soy el nodo maestro"
            for node in NODES:
                if node[0] != mi_ip:  # No enviar a sí mismo
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                            sock.sendto(msg.encode(), node)
                    except Exception as e:
                        print(f"Error al enviar heartbeat a {node}: {e}")
            next_heartbeat_time = current_time + HEARTBEAT_INTERVAL
        # Esperar un tiempo muy breve para evitar un uso elevado de CPU
        time.sleep(0.1)

# Función para recibir heartbeats y actualizar el estado de los nodos
def receive_heartbeats():
    global maestro_actual, soy_el_maestro
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            mensaje = data.decode()
            last_heartbeat[addr] = time.time()

            with master_lock:  # Asegurar la atomicidad de la actualización del estado del maestro
                if "soy el nodo maestro" in mensaje:
                    if addr[0] != maestro_actual and (not maestro_actual or addr[0] > maestro_actual):
                        actualizar_estado_maestro(addr[0])
                elif mi_ip > addr[0] and not hay_maestro_activo():
                    declarar_como_maestro()
        except socket.timeout:
            pass
        verificar_nodos_inactivos()



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

def verificar_nodos_inactivos():
    global maestro_actual, soy_el_maestro
    current_time = time.time()
    inactivos = []
    with master_lock:  # Asegurar la atomicidad de la comprobación de nodos inactivos
        for node, last_time in last_heartbeat.items():
            if current_time - last_time > MAX_INACTIVE_TIME:
                inactivos.append(node)
        
        for node in inactivos:
            if node[0] == maestro_actual:
                print(f"El nodo maestro {node} ha dejado de estar activo")
                maestro_actual = None
                if mi_ip == node[0]:
                    soy_el_maestro = False
            print(f"{node} ha dejado de estar activo")
            del last_heartbeat[node]  # Eliminar el nodo inactivo del registro


# Configuración inicial del nodo
interfaz = "ens33"  # Asegúrate de que esta interfaz es la correcta
mi_ip = obtener_direccion_ip(interfaz)
if mi_ip == "No se pudo obtener la dirección IP":
    raise Exception("No se pudo determinar la dirección IP del nodo")

# Añade tu dirección IP a la lista de nodos si no está presente
if (mi_ip, 5000) not in NODES:
    NODES.append((mi_ip, 5000))

# Creación y configuración del socket UDP para recibir
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((mi_ip, 5000))
sock.settimeout(1)

# Iniciar hilos para enviar y recibir heartbeats
send_thread = threading.Thread(target=send_heartbeats)
receive_thread = threading.Thread(target=receive_heartbeats)
send_thread.start()
receive_thread.start()

# No es necesario unir los hilos al principal si se desea que el programa continúe ejecutando otras tareas
# Si el script debe mantenerse en ejecución, puedes usar un bucle aquí

