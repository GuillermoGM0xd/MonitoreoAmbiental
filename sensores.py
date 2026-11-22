# Clases para leer DHT11, PMS7003, BMP280 y el anemómetro (MicroPython/ESP32).
# Cada lectura devuelve None si el sensor falla, nunca detiene el programa.

import time
import struct
import dht  
from machine import Pin, UART, I2C  
import config


# DHT11
class SensorDHT11:
    def __init__(self):
        self.sensor = dht.DHT11(Pin(config.PIN_DHT11))

    def leer(self):
        try:
            self.sensor.measure()
            return {"temperatura": self.sensor.temperature(),
                    "humedad": self.sensor.humidity()}
        except OSError:
            return None


# PMS7003
class SensorPMS7003:
    def __init__(self):
        self.uart = UART(config.UART_PMS, baudrate=9600,
                         tx=config.PIN_PMS_TX, rx=config.PIN_PMS_RX)

    def leer(self, timeout_ms=3000):
        """Busca una trama de 32 bytes (cabecera 0x42 0x4D) y verifica
        su suma de comprobación antes de aceptarla."""
        self.uart.read()  # vaciar datos viejos
        buf = b""
        inicio = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), inicio) < timeout_ms:
            datos = self.uart.read()
            if datos:
                buf += datos
            i = buf.find(b"\x42\x4d")
            if i >= 0 and len(buf) - i >= 32:
                trama = buf[i:i + 32]
                esperado = struct.unpack(">H", trama[30:32])[0]
                if sum(trama[:30]) == esperado:
                    # Bytes 12-13: PM2.5 y 14-15: PM10 (valores atmosféricos)
                    pm2_5, pm10 = struct.unpack(">HH", trama[12:16])
                    return {"pm2_5": pm2_5, "pm10": pm10}
                buf = buf[i + 2:]  # trama corrupta, seguir buscando
            time.sleep_ms(50)
        return None


# BMP280
class SensorBMP280:
    def __init__(self):
        self.i2c = I2C(0, sda=Pin(config.PIN_I2C_SDA),
                       scl=Pin(config.PIN_I2C_SCL), freq=100000)
        self.dir = config.DIRECCION_BMP280
        self.listo = False
        try:
            if self.i2c.readfrom_mem(self.dir, 0xD0, 1)[0] != 0x58:
                return  # no es un BMP280
            # Coeficientes de calibración de fábrica (24 bytes)
            c = struct.unpack("<HhhHhhhhhhhh",
                              self.i2c.readfrom_mem(self.dir, 0x88, 24))
            self.T1, self.T2, self.T3 = c[0:3]
            self.P = c[3:12]  # P1..P9
            self.i2c.writeto_mem(self.dir, 0xF4, b"\x57")  # modo normal
            self.i2c.writeto_mem(self.dir, 0xF5, b"\x10")
            self.listo = True
        except OSError:
            pass

    def leer(self):
        if not self.listo:
            return None
        try:
            d = self.i2c.readfrom_mem(self.dir, 0xF7, 6)
        except OSError:
            return None
        adc_p = (d[0] << 12) | (d[1] << 4) | (d[2] >> 4)
        adc_t = (d[3] << 12) | (d[4] << 4) | (d[5] >> 4)

        # Compensación de temperatura (fórmula del fabricante)
        v1 = (adc_t / 16384.0 - self.T1 / 1024.0) * self.T2
        v2 = ((adc_t / 131072.0 - self.T1 / 8192.0) ** 2) * self.T3
        t_fine = v1 + v2
        temp = t_fine / 5120.0

        # Compensación de presión
        P1, P2, P3, P4, P5, P6, P7, P8, P9 = self.P
        v1 = t_fine / 2.0 - 64000.0
        v2 = v1 * v1 * P6 / 32768.0 + v1 * P5 * 2.0
        v2 = v2 / 4.0 + P4 * 65536.0
        v1 = (P3 * v1 * v1 / 524288.0 + P2 * v1) / 524288.0
        v1 = (1.0 + v1 / 32768.0) * P1
        if v1 == 0:
            return None
        p = (1048576.0 - adc_p - v2 / 4096.0) * 6250.0 / v1
        v1 = P9 * p * p / 2147483648.0
        v2 = p * P8 / 32768.0
        p = p + (v1 + v2 + P7) / 16.0
        return {"presion": round(p / 100.0, 2), "temp_bmp": round(temp, 2)}


# Anemómetro
class Anemometro:
    """Cuenta pulsos con una interrupción y los convierte a km/h."""

    def __init__(self):
        self.pulsos = 0
        self.ultimo = 0
        self.pin = Pin(config.PIN_ANEMOMETRO, Pin.IN, Pin.PULL_UP)
        self.pin.irq(trigger=Pin.IRQ_FALLING, handler=self._pulso)

    def _pulso(self, pin):
        ahora = time.ticks_ms()
        # Anti-rebote: ignora pulsos separados por menos de 5 ms
        if time.ticks_diff(ahora, self.ultimo) > 5:
            self.pulsos += 1
            self.ultimo = ahora

    def leer(self, ventana_s=None):
        ventana_s = ventana_s or config.VENTANA_VIENTO_S
        self.pulsos = 0
        time.sleep(ventana_s)
        frecuencia = self.pulsos / ventana_s  # pulsos por segundo
        return {"viento": round(frecuencia * config.PULSOS_A_KMH, 2)}
