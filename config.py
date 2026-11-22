# Parámetros centrales de la estación. Si algo cambia (pines, intervalo,
# calibración del anemómetro), se modifica solo aquí.

ESTACION_ID = "ITE-N01"

# Pines del ESP32 
PIN_DHT11 = 4            # Dato del DHT11
PIN_ANEMOMETRO = 27      # Salida de pulsos del anemómetro
PIN_I2C_SDA = 21         # BMP280
PIN_I2C_SCL = 22         # BMP280
UART_PMS = 2             # UART2 del ESP32
PIN_PMS_TX = 17          # TX del ESP32 -> RX del PMS7003
PIN_PMS_RX = 16          # RX del ESP32 <- TX del PMS7003

# Muestreo 
INTERVALO_MUESTREO_S = 60   # Tiempo entre lecturas completas
VENTANA_VIENTO_S = 5        # Tiempo que se cuentan pulsos del anemómetro

# Calibración 
# Se asume anemómetro de pulsos (reed o Hall). Con 1 pulso/s = 2.4 km/h
# (valor estandar). 
PULSOS_A_KMH = 2.4
DIRECCION_BMP280 = 0x76     # Puede ser 0x77 según el módulo

# Almacenamiento 
ARCHIVO_CSV = "lecturas.csv"

# Rangos físicamente válidos (mínimo, máximo) 
RANGOS = {
    "temperatura": (0, 50),        # Rango del DHT11
    "humedad": (20, 90),           # Rango del DHT11
    "pm2_5": (0, 500),             # Rango del PMS7003
    "pm10": (0, 500),
    "presion": (300, 1100),        # hPa, rango del BMP280
    "temp_bmp": (-40, 85),
    "viento": (0, 150),            # km/h
}
