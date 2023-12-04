import socket
import threading
import time
import subprocess



mensajes_para_guardar = []
registro_actividad = {} 
lista_nodos = ["192.168.192."]

def enviar_heartbeat():
    while True:
        mensaje_heartbeat = "HEARTBEAT"
        for destino_ip in lista_nodos:  # Asegúrate de definir esta lista
            s.sendto(mensaje_heartbeat.encode('utf-8'), (destino_ip, mi_puerto))
        time.sleep(5)  # Intervalo de tiempo entre heartbeats (ajustar según sea necesario)


def monitorear_nodos():
    while True:
        tiempo_actual = time.time()
        for nodo, ultimo_heartbeat in list(registro_actividad.items()):
            if tiempo_actual - ultimo_heartbeat > 10:  # Umbral de tiempo (ajustar según sea necesario)
                print(f"Nodo {nodo} no responde")
                del registro_actividad[nodo]
        time.sleep(5)  # Intervalo de tiempo para el monitoreo




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
    mensaje_completo = ""  # Inicializa mensaje_completo al principio
    while True:
        try:
            mensaje_recibido, direccion = s.recvfrom(1024)
            if mensaje_recibido.decode('utf-8') == "HEARTBEAT":
                registro_actividad[direccion] = time.time()
            else:
                mensaje_decodificado = mensaje_recibido.decode('utf-8')
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                mensaje_completo = f"{timestamp} - Mensaje RECIBIDO de {direccion}: {mensaje_decodificado}"
                mensajes_para_guardar.append(mensaje_completo)
            
            if not mensaje_confirmado and mensaje_completo:
                # Enviar un mensaje de confirmación al remitente
                confirmacion = "Confirmo la recepcion de tu mensaje"
                s.sendto(confirmacion.encode('utf-8'), direccion)
                print(mensaje_completo)  # Ahora esto no causará error porque mensaje_completo está inicializado
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

# Crea hilos para recibir, enviar y guardar mensajes

thread_recibir = threading.Thread(target=recibir_mensajes)
thread_enviar = threading.Thread(target=enviar_mensajes)
thread_guardar = threading.Thread(target=guardar_mensajes)
thread_heartbeat = threading.Thread(target=enviar_heartbeat)
thread_monitorear = threading.Thread(target=monitorear_nodos)
# Que corran en segundo plano
thread_recibir.daemon = True
thread_enviar.daemon = True
thread_guardar.daemon = True

for thread in [thread_recibir, thread_enviar, thread_guardar, thread_heartbeat, thread_monitorear]:
    thread.daemon = True
    thread.start()

# El programa principal no hace nada más que esperar
while True:
    pass
