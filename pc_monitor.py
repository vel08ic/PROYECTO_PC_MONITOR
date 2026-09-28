# Importamos 'psutil' (Process and System Utilities), la librería estándar de facto en Python 
# para monitorizar rendimiento, procesos y hardware del sistema operativo.
import psutil

# Importamos 'time', que nos permite controlar tiempos de espera y pausas en la ejecución.
import time

# Importamos 'os' para comprobar variables del sistema operativo de forma nativa.
import os


def obtener_uso_cpu():
    """
    Mide el porcentaje de uso total de la CPU.
    """
    # psutil.cpu_percent(interval=1) toma una muestra del uso de la CPU dejando pasar 
    # 1 segundo de margen para calcular una media real y precisa (en lugar de un valor instantáneo de 0%).
    uso_total = psutil.cpu_percent(interval=1)
    return uso_total


def obtener_uso_memoria():
    """
    Obtiene estadísticas detalladas de la memoria RAM instalada.
    """
    # psutil.virtual_memory() devuelve un objeto con métricas de la memoria física.
    memoria = psutil.virtual_memory()
    return {
        # Convertimos los bytes totales a Gigabytes dividiendo entre 1024 tres veces (1024^3).
        "total_gb": memoria.total / (1024 ** 3),
        "disponible_gb": memoria.available / (1024 ** 3),
        "porcentaje": memoria.percent
    }


def obtener_uso_disco(punto_montaje="C:\\" if os.name == "nt" else "/"):
    """
    Obtiene estadísticas de almacenamiento del disco principal.
    Por defecto detecta si estás en Windows ('C:\\') o en Linux/macOS ('/').
    """
    disco = psutil.disk_usage(punto_montaje)
    return {
        "total_gb": disco.total / (1024 ** 3),
        "libre_gb": disco.free / (1024 ** 3),
        "porcentaje": disco.percent
    }


def obtener_temperaturas():
    """
    Intenta leer los sensores térmicos de la placa base o del procesador.
    """
    temperaturas = {}
    try:
        # psutil.sensors_temperatures() lee los sensores de hardware expuestos por el S.O.
        sensores = psutil.sensors_temperatures()
        if sensores:
            for nombre, entradas in sensores.items():
                for entrada in entradas:
                    # Guardamos el nombre del sensor y su temperatura actual en grados Celsius
                    temperaturas[f"{nombre} - {entrada.label or 'Core'}"] = entrada.current
    except (AttributeError, NotImplementedError):
        # En ciertos entornos (como Windows en según qué placas, WSL o contenedores Docker), 
        # esta función no está implementada o no devuelve atributos válidos. 
        # Capturamos el error para que el script no se rompa.
        pass
    return temperaturas


def obtener_red():
    """
    Mide el tráfico acumulado de red (bytes enviados y recibidos) 
    desde que se encendió el equipo o se reinició la interfaz.
    """
    red = psutil.net_io_counters()
    return {
        # Convertimos los bytes a Megabytes dividiendo entre 1024^2.
        "enviados_mb": red.bytes_sent / (1024 ** 2),
        "recibidos_mb": red.bytes_recv / (1024 ** 2)
    }


def main():
    """
    Función principal que ejecuta el bucle continuo de monitorización.
    """
    print("=== MONITOR DE RECURSOS DEL PC ===")
    print("Iniciando monitorización en tiempo real (Presiona Ctrl+C para salir)...\n")
    
    try:
        # Bucle infinito que mantendrá el monitor activo refrescando los datos.
        while True:
            # Recopilamos todas las métricas llamando a nuestras funciones
            cpu = obtener_uso_cpu()
            memoria = obtener_uso_memoria()
            disco = obtener_uso_disco()
            temperaturas = obtener_temperaturas()
            red = obtener_red()
            
            # Imprimimos un panel formateado en la terminal
            print("\n" + "=" * 50)
            print(f"🔥 CPU Uso Total: {cpu}%")
            print(f"🧠 Memoria RAM:   {memoria['porcentaje']}% usada ({memoria['disponible_gb']:.2f} GB libres de {memoria['total_gb']:.2f} GB)")
            print(f"💾 Disco Principal: {disco['porcentaje']}% usado ({disco['libre_gb']:.2f} GB libres de {disco['total_gb']:.2f} GB)")
            
            if temperaturas:
                print("🌡️ Temperaturas:")
                for sensor, temp in temperaturas.items():
                    print(f"   - {sensor}: {temp}°C")
            else:
                print("🌡️ Temperaturas: No disponibles en este S.O. o hardware.")
                
            print(f"🌐 Tráfico de Red -> Enviados: {red['enviados_mb']:.2f} MB | Recibidos: {red['recibidos_mb']:.2f} MB")
            
            # Pausa de 2 segundos antes de volver a recopilar datos para no saturar la CPU.
            time.sleep(2)
            
    except KeyboardInterrupt:
        # Captura la combinación de teclas Ctrl+C para salir de forma limpia y elegante.
        print("\n\n🛑 Monitor detenido por el usuario. ¡Hasta pronto!")


if __name__ == "__main__":
    main()