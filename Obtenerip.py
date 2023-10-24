import subprocess

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

if __name__ == "__main__":
    interfaz = "eth0"  # Reemplaza con el nombre de la interfaz que deseas consultar
    direccion_ip = obtener_direccion_ip(interfaz)

    if direccion_ip:
        print(f"La dirección IP (inet) de la interfaz {interfaz} es: {direccion_ip}")
    else:
        print("No se pudo obtener la dirección IP.")
