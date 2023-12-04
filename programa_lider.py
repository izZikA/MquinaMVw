import socket
import threading
import time
import subprocess

lista_de_nodos = ["192.168.192.1", "192.168.1.3", "192.168.1.4"]  # Ejemplo
estado_de_nodos = {nodo: False for nodo in lista_de_nodos}  # False significa 'no confirmado'



mensajes_para_guardar = []

def seleccionar_lider(direccion_nueva, lider_actual):
    if not lider_actual or direccion_nueva > lider_actual:
        return direccion_nueva
    return lider_actual



def enviar_heartbeats():
    while True:
        for nodo in lista_de_nodos:
            try:
                s.sendto("heartbeat".encode('utf-8'), (nodo, mi_puerto))
            except Exception as e:
                print(f"No se pudo enviar heartbeat a {nodo}: {e}")
        time.sleep(5)  # Enviar heartbeats cada 5 segundos, por ejemplo



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

            if mensaje_decodificado == "heartbeat":
                estado_de_nodos[direccion[0]] = True
            else:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                mensaje_completo = f"{timestamp} - Mensaje RECIBIDO de {direccion}: {mensaje_decodificado}"
                mensajes_para_guardar.append(mensaje_completo)
            #print(mensaje_completo)
            
            if not mensaje_confirmado:
                # Enviar un mensaje de confirmación al remitente
                confirmacion = "Confirmo la recepcion de tu mensaje"
                s.sendto(confirmacion.encode('utf-8'), direccion)
                print(mensaje_completo)
                mensaje_confirmado=True
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
        destino_ip = input("Ingrese la dirección IP de destino: ")
        mensaje = input("Ingrese su mensaje: ")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        mensaje_completo = f"{timestamp} - Mensaje ENVIADO a {destino_ip}: {mensaje}"
        #print(mensaje_completo)
        
        # Envía el mensaje a la dirección IP de destino especificada
        destino_puerto = 12345  # Se queda en 12345 para que no haya fallas
        s.sendto(mensaje.encode('utf-8'), (destino_ip, destino_puerto))
        mensajes_para_guardar.append(mensaje_completo)


def verificar_nodos():
    while True:
        # Espera un tiempo suficiente para recibir heartbeats
        time.sleep(6)

        # Restablece todos los estados de nodos a False
        for nodo in lista_de_nodos:
            estado_de_nodos[nodo] = False

        # Espera un poco para dar tiempo a los heartbeats de llegar
        time.sleep(1)

        # Ahora verifica y reporta el estado actualizado de cada nodo
        for nodo in lista_de_nodos:
            if estado_de_nodos[nodo]:
                print(f"Nodo {nodo} está vivo.")
            else:
                print(f"Nodo {nodo} podría estar caído.")


# Configura la dirección y el puerto en esta máquina virtual
# Se cambia conforme el ip de la maquina virtual
interfaz = "ens33"  # Reemplaza con el nombre de la interfaz que deseas consultar
mi_ip = obtener_direccion_ip(interfaz)
if mi_ip:
   print(f"La dirección IP (inet) de la interfaz {interfaz} es: {mi_ip}")
else:
    print("No se pudo obtener la dirección IP.")
mi_puerto = 12345 

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((mi_ip, mi_puerto))
s.settimeout(1)

thread_enviar_heartbeats = threading.Thread(target=enviar_heartbeats)
thread_enviar_heartbeats.daemon = True
thread_enviar_heartbeats.start()

thread_verificar_nodos = threading.Thread(target=verificar_nodos)
thread_verificar_nodos.daemon = True
thread_verificar_nodos.start()


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

