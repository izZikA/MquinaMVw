import socket
import threading
import time
import subprocess


# Define un conjunto para realizar un seguimiento de los usuarios actuales
usuarios = set()

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
    
    
def recibir_mensajes():
    mensaje_confirmado = False
    while True:
        try:
            mensaje_recibido, direccion = s.recvfrom(1024)
            mensaje_decodificado = mensaje_recibido.decode('utf-8')
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            mensaje_completo = f"{timestamp} - Mensaje RECIBIDO de {direccion}: {mensaje_decodificado}"
            mensajes_para_guardar.append(mensaje_completo)
            
            if not mensaje_confirmado:
                # Enviar un mensaje de confirmación al remitente
                confirmacion = "Confirmo la recepción de tu mensaje"
                s.sendto(confirmacion.encode('utf-8'), direccion)
                print(mensaje_completo)
                mensaje_confirmado = True

        except socket.timeout:
            mensaje_confirmado = False

def guardar_mensajes():
    while True:
        if mensajes_para_guardar:
            mensaje_para_guardar = mensajes_para_guardar.pop(0)
            with open("logMensajes.txt", "a") as log_file:
                log_file.write(mensaje_para_guardar + "\n")
            time.sleep(1)  # Espera un segundo antes de intentar guardar el siguiente mensaje

def enviar_mensajes():
    while True:
        mensaje = input("Ingrese su mensaje: ")
        priv = 0

        for nombre, destino in usuarios:
            if nombre in mensaje:
                priv = 1
                if destino != mi_ip:
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    mensaje_completo = f"{timestamp} - Mensaje ENVIADO a {nombre}:{destino}: {mensaje}"
                    destino_puerto = 12345
                    s.sendto(mensaje.encode('utf-8'), (destino, destino_puerto))
                    mensajes_para_guardar.append(mensaje_completo)

        if priv == 0:
            if destino != mi_ip:
                for nombre, destino in usuarios:
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    mensaje_completo = f"{timestamp} - Mensaje ENVIADO a todos: {mensaje}"
                    destino_puerto = 12345
                    s.sendto(mensaje.encode('utf-8'), (destino, destino_puerto))
                    mensajes_para_guardar.append(mensaje_completo)


mensajes_para_guardar = []
#usuarios que estan en el chat

usuarios = {("/Debian1", "192.168.106.136"), ("/Debian2", "192.168.106.137"),
           ("/Debian3", "192.168.106.138"), ("/Debian4", "192.168.106.139"),
           ("/Debian5", "192.168.106.140")}
# Configura la dirección y el puerto en esta máquina virtual
# Se cambia conforme el ip de la maquina virtual

interface="ens33"
mi_ip = obtener_direccion_ip(interface)
mi_puerto = 12345 

if mi_ip:
    print(f"La dirección IP (inet) de la interfaz {interface} es: {mi_ip}")
else:
    print("No se pudo obtener la dirección IP.")

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((mi_ip, mi_puerto))
s.settimeout(1)

# Crea hilos para recibir, enviar y guardar mensajes
thread_recibir = threading.Thread(target=recibir_mensajes)
thread_enviar = threading.Thread(target=enviar_mensajes)
thread_guardar = threading.Thread(target=guardar_mensajes)

# Que corran en segundo plano
thread_recibir.daemon = True
thread_enviar.daemon = True
thread_guardar.daemon = True

# Los inicializa
thread_recibir.start()
thread_enviar.start()
thread_guardar.start()

# El programa principal no hace nada más que esperar
while True:
    pass
