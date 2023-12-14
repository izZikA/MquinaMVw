import socket
import threading
import time
import json

# Definición de la clase Producto
class Producto:
    def __init__(self, id, articulo, categoria, precio, cantidad):
        self.id = id
        self.articulo = articulo
        self.categoria = categoria
        self.precio = precio
        self.cantidad = cantidad

    def __str__(self):
        return f"{self.id}: {self.articulo} - {self.categoria} - ${self.precio} - Cantidad: {self.cantidad}"

# Definición de la clase Inventario
class Inventario:
    def __init__(self, datos_json):
        self.productos = {id: Producto(id, **datos) for id, datos in datos_json.items()}

    def mostrar_productos(self):
        for producto in self.productos.values():
            print(producto)

    def vender_producto(self, id_producto, cantidad):
        if id_producto in self.productos and self.productos[id_producto].cantidad >= cantidad:
            self.productos[id_producto].cantidad -= cantidad
            print(f"Vendido: {cantidad} de {self.productos[id_producto].articulo}")
            return True
        else:
            print("Producto no disponible o cantidad insuficiente")
            return False

    def actualizar_producto(self, id_producto, cantidad_vendida):
        if id_producto in self.productos:
            self.productos[id_producto].cantidad -= cantidad_vendida

# Definición de la clase Nodo
class Nodo:
    def __init__(self, ip, puerto, inventario):
        self.ip = ip
        self.puerto = puerto
        self.inventario = inventario
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((ip, puerto))
        self.sock.settimeout(1)
        self.es_maestro = False
        self.ultimo_heartbeat = time.time()

    def enviar_heartbeat(self):
        while True:
            try:
                for nodo in NODES:
                    if nodo != (self.ip, self.puerto):
                        self.sock.sendto(b"Heartbeat", nodo)
            except Exception as e:
                print(f"Error al enviar heartbeat: {e}")
            time.sleep(HEARTBEAT_INTERVAL)

    def recibir_heartbeat_y_actualizaciones(self):
        global master_node
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                if addr != (self.ip, self.puerto):
                    if "venta" in data.decode():
                        self.procesar_actualizacion_inventario(data.decode())
                    else:
                        self.ultimo_heartbeat = time.time()
            except socket.timeout:
                pass

    def iniciar(self):
        threading.Thread(target=self.enviar_heartbeat).start()
        threading.Thread(target=self.recibir_heartbeat_y_actualizaciones).start()

    def vender_producto(self, id_producto, cantidad):
        if self.inventario.vender_producto(id_producto, cantidad):
            self.notificar_cambio_inventario(id_producto, cantidad)

    def notificar_cambio_inventario(self, id_producto, cantidad):
        msg = json.dumps({"venta": True, "id": id_producto, "cantidad": cantidad})
        for nodo in NODES:
            if nodo != (self.ip, self.puerto):
                self.sock.sendto(msg.encode(), nodo)

    def procesar_actualizacion_inventario(self, data):
        info_venta = json.loads(data)
        id_producto = info_venta["id"]
        cantidad_vendida = info_venta["cantidad"]
        self.inventario.actualizar_producto(id_producto, cantidad_vendida)

# Configuraciones de la red
NODES = [("192.168.106.135", 5000), ("192.168.106.137", 5000), ("192.168.106.138", 5000)]
HEARTBEAT_INTERVAL = 5
MAX_INACTIVE_TIME = 15
master_node = None

# Funciones adicionales
def obtener_ip_local():
    return "192.168.106.135"  # Cambiar esto según la configuración de tu red

# Ejemplo de uso
if __name__ == "__main__":
    try:
        datos_json = {
    "101": {
    "articulo": "Playera",
    "categoria": "Ropa",
    "precio": 500,
    "cantidad": 50,
    "Inv1": 0,
    "Inv2": 0,
    "Inv3": 0,
    "Inv4": 0,
    "Inv5": 0
  },
  "102": {
    "articulo": "Pantalon",
    "categoria": "Ropa",
    "precio": 1000,
    "cantidad": 50,
    "Inv1": 0,
    "Inv2": 0,
    "Inv3": 0,
    "Inv4": 0,
    "Inv5": 0
  },
  "103": {
    "articulo": "Tenis",
    "categoria": "Calzado",
    "precio": 1500,
    "cantidad": 30,
    "Inv1": 0,
    "Inv2": 0,
    "Inv3": 0,
    "Inv4": 0,
    "Inv5": 0
  },
  "104": {
    "articulo": "Mochila",
    "categoria": "Accesorio",
    "precio": 3000,
    "cantidad": 30,
    "Inv1": 0,
    "Inv2": 0,
    "Inv3": 0,
    "Inv4": 0,
    "Inv5": 0
  },
  "105": {
    "articulo": "Celular",
    "categoria": "Tecnologia",
    "precio": 8000,
    "cantidad": 15,
    "Inv1": 0,
    "Inv2": 0,
    "Inv3": 0,
    "Inv4": 0,
    "Inv5": 0
  },
  "106": {
    "articulo": "Xbox",
    "categoria": "Tecnologia",
    "precio": 11000,
    "cantidad": 8,
    "Inv1": 0,
    "Inv2": 0,
    "Inv3": 0,
    "Inv4": 0,
    "Inv5": 0
  },
  "107": {
    "articulo": "Playstation",
    "categoria": "Tecnologia",
    "precio": 12000,
    "cantidad": 8,
    "Inv1": 0,
    "Inv2": 0,
    "Inv3": 0,
    "Inv4": 0,
    "Inv5": 0
  },
  "108": {
    "articulo": "Laptop",
    "categoria": "Tecnologia",
    "precio": 10000,
    "cantidad": 12,
    "Inv1": 0,
    "Inv2": 0,
    "Inv3": 0,
    "Inv4": 0,
    "Inv5": 0
  },
  "109": {
    "articulo": "Camisa Casual",
    "categoria": "Ropa",
    "precio": 600,
    "cantidad": 40,
    "Inv1": 0,
    "Inv2": 0,
    "Inv3": 0,
    "Inv4": 0,
    "Inv5": 0
  },
  "110": {
    "articulo": "Jeans",
    "categoria": "Ropa",
    "precio": 1200,
    "cantidad": 35,
    "Inv1": 0,
    "Inv2": 0,
    "Inv3": 0,
    "Inv4": 0,
    "Inv5": 0
  },
  "111": {
    "articulo": "Zapatos Deportivos",
    "categoria": "Calzado",
    "precio": 1800,
    "cantidad": 25,
    "Inv1": 0,
    "Inv2": 0,
    "Inv3": 0,
    "Inv4": 0,
    "Inv5": 0
  },
  "112": {
    "articulo": "Bolso de Moda",
    "categoria": "Accesorio",
    "precio": 2500,
    "cantidad": 20,
    "Inv1": 0,
    "Inv2": 0,
    "Inv3": 0,
    "Inv4": 0,
    "Inv5": 0
  },
  "113": {
    "articulo": "Smartwatch",
    "categoria": "Tecnologia",
    "precio": 3500,
    "cantidad": 10,
    "Inv1": 0,
    "Inv2": 0,
    "Inv3": 0,
    "Inv4": 0,
    "Inv5": 0
  },
  "114": {
    "articulo": "Consola de Juegos Portátil",
    "categoria": "Tecnologia",
    "precio": 8000,
    "cantidad": 5,
    "Inv1": 0,
    "Inv2": 0,
    "Inv3": 0,
    "Inv4": 0,
    "Inv5": 0
  },
  "115": {
    "articulo": "Auriculares Inalámbricos",
    "categoria": "Tecnologia",
    "precio": 1200,
    "cantidad": 15,
    "Inv1": 0,
    "Inv2": 0,
    "Inv3": 0,
    "Inv4": 0,
    "Inv5": 0
  },
  "116": {
    "articulo": "Mesa Plegable",
    "categoria": "Muebles",
    "precio": 1500,
    "cantidad": 20,
    "Inv1": 0,
    "Inv2": 0,
    "Inv3": 0,
    "Inv4": 0,
    "Inv5": 0
  },
  "117": {
    "articulo": "Plancha de Ropa",
    "categoria": "Electrodomésticos",
    "precio": 700,
    "cantidad": 30,
    "Inv1": 0,
    "Inv2": 0,
    "Inv3": 0,
    "Inv4": 0,
    "Inv5": 0
  },
  "118": {
    "articulo": "Set de Toallas",
    "categoria": "Baño",
    "precio": 400,
    "cantidad": 25,
    "Inv1": 0,
    "Inv2": 0,
    "Inv3": 0,
    "Inv4": 0,
    "Inv5": 0
  }
}       
        inventario = Inventario(datos_json)
        mi_nodo = Nodo(obtener_ip_local(), 5000, inventario)
        mi_nodo.iniciar()

        # Interfaz de usuario para el nodo (ejemplo simplificado)
        while True:
            print("\n1. Mostrar productos\n2. Vender producto\n3. Salir")
            opcion = input("Elige una opción: ")
            if opcion == "1":
                inventario.mostrar_productos()
            elif opcion == "2":
                id_producto = input("ID del producto: ")
                cantidad = int(input("Cantidad: "))
                mi_nodo.vender_producto(id_producto, cantidad)
            elif opcion == "3":
                break
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")
    finally:
        print("Liberando recursos...")
        mi_nodo.sock.close()
        print("Recursos liberados. Programa terminado.")

