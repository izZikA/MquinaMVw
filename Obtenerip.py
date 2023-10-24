# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 08:14:15 2023

@author: migue
"""

import socket

def obtener_direccion_ip():
    try:
        # Obtiene la dirección IP del host local
        direccion_ip = socket.gethostbyname(socket.gethostname())
        return direccion_ip
    except:
        return None

# Llama a la función para obtener la dirección IP
direccion_ip = obtener_direccion_ip()

if direccion_ip:
    print(f"La dirección IP local es: {direccion_ip}")
else:
    print("No se pudo obtener la dirección IP.")
