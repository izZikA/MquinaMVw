import socket
import threading
import time
import subprocess

# Direcciones IP y puertos de los nodos en la red
NODES = [("192.168.106.135", 5000), ("192.168.106.137", 5000), ("192.168.106.138", 5000)]  # Asegúrate de ajustar estas direcciones IP
# Intervalo en segundos para enviar heartbeats
HEARTBEAT_INTERVAL = 5
# Tiempo máximo en segundos para considerar un nodo como inactivo
MAX_INACTIVE_TIME = 15

# Esta función envía heartbeats a todos los nodos
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

# Esta función recibe heartbeats y actualiza el estado de los nodos
def receive_heartbeats():
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            mensaje = data.decode()
            print(f"Heartbeat recibido de {addr}, mensaje: {mensaje}")
            last_heartbeat[addr] = time.time()
            if "soy el nodo maestro" in mensaje:
                actualizar_estado_maestro(addr)
            elif mi_ip > addr[0] and not hay_maestro_activo():
                declarar_como_maestro()
        except socket.timeout:
            pass

        # Verificar nodos inactivos
        verificar_nodos_inactivos()

def actualizar_estado_maestro(addr):
    global maestro_actual
    maestro_actual = addr[0]

def declarar_como_maestro():
    global soy_el_maestro
    soy_el_maestro = True
    print(f"{mi_ip} se ha declarado como el nodo maestro")

def hay_maestro_activo():
    return maestro_actual and time.time() - last_heartbeat.get((maestro_actual, 5000), 0) < MAX_INACTIVE_TIME

def verificar_nodos_inactivos():
    current_time = time.time()
    for node in NODES:
        if current_time - last_heartbeat.get(node, 0) > MAX_INACTIVE_TIME:
            if node[0] == maestro_actual:
                print(f"El nodo maestro {node} ha dejado de estar activo")
                maestro_actual = None
            print(f"{node} ha dejado de estar activo")

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
    
# Inicialización
interfaz = "ens33"
mi_ip = obtener_direccion_ip(interfaz)
soy_el_maestro = False
maestro_actual = None

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
