import socket

def obtener_direccion_ip():
    try:
        
        # Obtenemos la dirección IP asociada al nombre del host
        direccion_ip = socket.gethostbyname(ens33)
        return direccion_ip
    except socket.error as e:
        return str(e)

# Llamamos a la función para obtener la dirección IP y la imprimimos
ip = obtener_direccion_ip()
print(f"La dirección IP de la red local es: {ip}")

