# Programa principal: lee los sensores, valida y guarda en CSV.
# MicroPython ejecuta main.py automáticamente al encender el ESP32.

import time
import os
import config
from sensores import SensorDHT11, SensorPMS7003, SensorBMP280, Anemometro
from validacion import combinar, validar, resumen_estado

# Orden de las columnas del archivo CSV
VARIABLES = ["temperatura", "humedad", "pm2_5", "pm10",
             "presion", "temp_bmp", "viento"]


def marca_de_tiempo():
    t = time.localtime()
    return "%04d-%02d-%02d %02d:%02d:%02d" % t[:6]


def preparar_csv():
    """Crea el archivo con encabezados si todavía no existe."""
    try:
        os.stat(config.ARCHIVO_CSV)
    except OSError:
        with open(config.ARCHIVO_CSV, "w") as f:
            columnas = ["fecha", "estacion"]
            for v in VARIABLES:
                columnas += [v, v + "_estado"]
            f.write(",".join(columnas) + "\n")


def guardar(validadas):
    fila = [marca_de_tiempo(), config.ESTACION_ID]
    for v in VARIABLES:
        valor, estado = validadas[v]
        fila += ["" if valor is None else str(valor), estado]
    with open(config.ARCHIVO_CSV, "a") as f:
        f.write(",".join(fila) + "\n")


def mostrar(validadas):
    print("-" * 40)
    print(marca_de_tiempo(), "|", resumen_estado(validadas))
    for v in VARIABLES:
        valor, estado = validadas[v]
        print("  %-12s %-8s %s" % (v, valor, estado))


def main():
    print("Iniciando estacion", config.ESTACION_ID)
    dht11 = SensorDHT11()
    pms = SensorPMS7003()
    bmp = SensorBMP280()
    viento = Anemometro()
    preparar_csv()

    while True:
        inicio = time.ticks_ms()

        # Cada sensor es independiente: si uno falla, los demás siguen
        lectura = combinar(dht11.leer(), pms.leer(), bmp.leer(), viento.leer())
        validadas = validar(lectura)
        mostrar(validadas)
        guardar(validadas)

        # Espera lo que falte para completar el intervalo de muestreo
        transcurrido = time.ticks_diff(time.ticks_ms(), inicio) // 1000
        time.sleep(max(1, config.INTERVALO_MUESTREO_S - transcurrido))


main()
