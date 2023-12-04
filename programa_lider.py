import socket
import threading
import time
import subprocess

mensajes_para_guardar = []
nodos_conocidos = ["192.168.192.", "192.168.192."]  # Lista de nodos conocidos

def obtener_direccion_ip(interface):
    # ... Misma función existente ...

def recibir_mensajes():
    while True:
        try:
            mensaje_recibido, direccion = s.recvfrom(1024)
            mensaje_decodificado = mensaje_recibido.decode('utf-8')
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            if mensaje_decodificado == "heartbeat":
                responder_heartbeat(direccion)
                mensaje_completo = f"{timestamp} - Heartbeat RECIBIDO de {direccion}"
            else:
                mensaje_completo = f"{timestamp} - Mensaje RECIBIDO de {direccion}: {mensaje_decodificado}"
            
            mensajes_para_guardar.append(mensaje_completo)
            print(mensaje_completo)

        except socket.timeout:
            continue

def responder_heartbeat(direccion):
    confirmacion = "Heartbeat recibido"
    s.sendto(confirmacion.encode('utf-8'), direccion)

def guardar_mensajes():
    while True:
        if mensajes_para_guardar:
            mensaje_para_guardar = mensajes_para_guardar.pop(0)
            with open("logMensajes.txt", "a") as log_file:
                log_file.write(mensaje_para_guardar + "\n")
            time.sleep(1)

def enviar_heartbeat():
    while True:
        for nodo in nodos_conocidos:
            if nodo != mi_ip:  # No enviar a sí mismo
                s.sendto("heartbeat".encode('utf-8'), (nodo, mi_puerto))
        time.sleep(30)  # Enviar heartbeat cada 30 segundos

def enviar_mensajes():
    while True:
        destino_ip = input("Ingrese la dirección IP de destino: ")
        mensaje = input("Ingrese su mensaje: ")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        mensaje_completo = f"{timestamp} - Mensaje ENVIADO a {destino_ip}: {mensaje}"
        s.sendto(mensaje.encode('utf-8'), (destino_ip, mi_puerto))
        mensajes_para_guardar.append(mensaje_completo)

# Configuración inicial
interfaz = "ens33"  # Cambiar según la interfaz de red
mi_ip = obtener_direccion_ip(interfaz)
if mi_ip:
    print(f"La dirección IP (inet) de la interfaz {interfaz} es: {mi_ip}")
else:
    print("No se pudo obtener la dirección IP.")
mi_puerto = 12345 

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((mi_ip, mi_puerto))
s.settimeout(1)

# Creación e inicio de hilos
thread_recibir = threading.Thread(target=recibir_mensajes)
thread_enviar = threading.Thread(target=enviar_mensajes)
thread_guardar = threading.Thread(target=guardar_mensajes)
thread_heartbeat = threading.Thread(target=enviar_heartbeat)

for thread in [thread_recibir, thread_enviar, thread_guardar, thread_heartbeat]:
    thread.daemon = True
    thread.start()

while True:
    pass

