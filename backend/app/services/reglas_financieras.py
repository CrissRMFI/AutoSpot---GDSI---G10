"""
Reglas financieras compartidas para reportes de propietarios.

MVP US 15D:
  - El propietario recibe el 80% del ingreso bruto.
  - La plataforma retiene el 20%.
  - Penalizaciones fuera de scope.
"""
from decimal import Decimal, ROUND_HALF_UP


PORCENTAJE_GANANCIA_PROPIETARIO = Decimal("0.80")
PORCENTAJE_COMISION_PLATAFORMA = Decimal("0.20")
MONTO_CENTAVOS = Decimal("0.01")
PORCENTAJE_CENTAVOS = Decimal("0.01")


def cuantizar_monto(valor: Decimal) -> Decimal:
    """Normaliza valores monetarios a dos decimales."""
    return Decimal(valor).quantize(MONTO_CENTAVOS, rounding=ROUND_HALF_UP)


def calcular_desglose_ganancias(ingreso_bruto: Decimal) -> dict[str, Decimal]:
    """Calcula comisión y ganancia neta desde el ingreso bruto."""
    ingreso = cuantizar_monto(ingreso_bruto)
    comision = cuantizar_monto(ingreso * PORCENTAJE_COMISION_PLATAFORMA)
    ganancia_neta = cuantizar_monto(ingreso * PORCENTAJE_GANANCIA_PROPIETARIO)

    return {
        "ingreso_bruto": ingreso,
        "comision_plataforma": comision,
        "ganancia_neta": ganancia_neta,
    }


def calcular_variacion_porcentual(
    actual: Decimal,
    comparacion: Decimal,
) -> tuple[Decimal | None, str]:
    """
    Retorna variación porcentual y dirección.

    Si el período de comparación es cero y el actual tiene ingresos, la variación
    porcentual es indefinida; se informa SIN_COMPARACION para que la UI no muestre
    un porcentaje engañoso.
    """
    actual = cuantizar_monto(actual)
    comparacion = cuantizar_monto(comparacion)

    if comparacion == 0:
        if actual == 0:
            return Decimal("0.00"), "SIN_CAMBIO"
        return None, "SIN_COMPARACION"

    variacion = ((actual - comparacion) / comparacion * Decimal("100")).quantize(
        PORCENTAJE_CENTAVOS,
        rounding=ROUND_HALF_UP,
    )

    if variacion > 0:
        return variacion, "SUBE"
    if variacion < 0:
        return abs(variacion), "BAJA"
    return Decimal("0.00"), "SIN_CAMBIO"
