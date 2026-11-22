# Revisa que cada lectura esté dentro de su rango físico válido.
# Las lecturas inválidas NO se borran: se marcan con estado "ERROR",
# para respetar los criterios de inclusión y exclusión de la metodología.

import config


def combinar(*lecturas):
    """Une los diccionarios de cada sensor en uno solo.
    Los sensores que fallaron (None) simplemente no aportan datos."""
    resultado = {}
    for lectura in lecturas:
        if lectura:
            resultado.update(lectura)
    return resultado


def validar(lectura):
    """Devuelve un diccionario {variable: (valor, estado)} para todas las
    variables esperadas. Estados: OK, ERROR (fuera de rango) o SIN_DATO."""
    resultado = {}
    for variable, (minimo, maximo) in config.RANGOS.items():
        valor = lectura.get(variable)
        if valor is None:
            resultado[variable] = (None, "SIN_DATO")
        elif minimo <= valor <= maximo:
            resultado[variable] = (valor, "OK")
        else:
            resultado[variable] = (valor, "ERROR")
    return resultado


def resumen_estado(validadas):
    """Cuenta cuántas variables salieron bien para el reporte en consola."""
    ok = sum(1 for _, estado in validadas.values() if estado == "OK")
    return "%d/%d variables validas" % (ok, len(validadas))
