import socket
import threading
import time
import subprocess

# Variables globales
mensajes_para_guardar = []
nodos_conocidos = set()
lider = None
mi_ip = None
mi_puerto = 12345

# Funciones definidas previamente
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
        return None

def actualizar_lider():
    global lider, nodos_conocidos
    if nodos_conocidos:
        lider_actual = lider
        lider = max(nodos_conocidos)
        if lider_actual != lider:
            print(f"El nuevo líder es: {lider}")

def enviar_heartbeats(s):
    global mi_ip, mi_puerto, nodos_conocidos
    while True:
        for ip in nodos_conocidos:
            if ip != mi_ip:
                s.sendto(f"Heartbeat desde {mi_ip}".encode('utf-8'), (ip, mi_puerto))
        time.sleep(5)

# Función modificada para recibir mensajes, heartbeats y actualizar el líder
def recibir_mensajes(s):
    global mensajes_para_guardar, nodos_conocidos
    while True:
        try:
            mensaje_recibido, direccion = s.recvfrom(1024)
            ip_nodo, _ = direccion
            mensaje_decodificado = mensaje_recibido.decode('utf-8')
            if mensaje_decodificado.startswith("Heartbeat"):
                nodos_conocidos.add(ip_nodo)
                actualizar_lider()
            else:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                mensaje_completo = f"{timestamp} - Mensaje RECIBIDO de {direccion}: {mensaje_decodificado}"
                mensajes_para_guardar.append(mensaje_completo)
                print(mensaje_completo)
                # Enviar confirmación de recepción
                confirmacion = "Mensaje recibido"
                s.sendto(confirmacion.encode('utf-8'), direccion)
        except socket.timeout:
            pass

def guardar_mensajes():
    while True:
        if mensajes_para_guardar:
            mensaje_para_guardar = mensajes_para_guardar.pop(0)
            with open("logMensajes.txt", "a") as log_file:
                log_file.write(mensaje_para_guardar + "\n")
            time.sleep(1)

def enviar_mensajes(s):
    global mi_puerto
    while True:
        destino_ip = input("Ingrese la dirección IP de destino: ")
        mensaje = input("Ingrese su mensaje: ")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        mensaje_completo = f"{timestamp} - Mensaje ENVIADO a {destino_ip}: {mensaje}"
        s.sendto(mensaje.encode('utf-8'), (destino_ip, mi_puerto))
        mensajes_para_guardar.append(mensaje_completo)

# Configuración inicial
interfaz = "ens33"
mi_ip = obtener_direccion_ip(interfaz)
if mi_ip:
    print(f"La dirección IP (inet) de la interfaz {interfaz} es: {mi_ip}")
    nodos_conocidos.add(mi_ip)
    lider = mi_ip  # Inicialmente, este nodo se considera líder hasta recibir heartbeats
else:
    print("No se pudo obtener la dirección IP.")
    exit(1)

# Creación y configuración del socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((mi_ip, mi_puerto))
s.settimeout(2)

# Creación y ejecución de hilos
thread_recibir = threading.Thread(target=recibir_mensajes, args=(s,))
thread_enviar = threading.Thread(target=enviar_mensajes, args=(s,))
thread_guardar = threading.Thread(target=guardar_mensajes)
thread_heartbeats = threading.Thread(target=enviar_heartbeats, args=(s,))

thread_recibir.daemon = True
thread_enviar.daemon = True
thread_guardar.daemon = True
thread_heartbeats.daemon = True

thread_recibir.start()
thread_enviar.start()
thread_guardar.start()
thread_heartbeats.start()


# El programa principal no hace nada más que esperar
while True:
    pass




