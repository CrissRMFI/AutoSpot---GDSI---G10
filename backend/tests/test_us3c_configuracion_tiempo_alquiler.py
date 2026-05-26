"""
Tests unitarios de Servicio — US 3C: Configuracion del tiempo de alquiler.

Metodología: TDD (Fase Roja).

Criterios de Aceptación cubiertos en esta suite:
    CA 1: Dado que el negocio establece un tiempo minimo de uso (1 dia),
          cuando el periodo definido entre el inicio y el fin es inferior a dicho umbral,
          entonces el sistema debe rechazar la solicitud.
    CA 2: Dado que se ha definido un periodo valido y coherente,
          cuando el sistema procesa la solicitud,
          entonces debe determinar la duracion total exacta, en horas y dias.
"""
import pytest
from datetime import datetime, timedelta

# Importamos una función que todavía no existe para forzar la falla (TDD Fase Roja)
from app.services.alquiler_service import calcular_tiempo_alquiler


class TestCA1_TiempoMinimoAlquiler:
    """
    Validaciones sobre el tiempo mínimo de alquiler (1 día).
    """

    def test_ca1_tiempo_menor_a_un_dia_es_rechazado(self):
        """Si el periodo es de menos de 24 horas, debe lanzar ValueError."""
        inicio = datetime(2025, 1, 1, 10, 0, 0)
        # 23 horas y 59 minutos
        fin = inicio + timedelta(hours=23, minutes=59)

        with pytest.raises(ValueError, match="El tiempo minimo de alquiler es de 1 dia"):
            calcular_tiempo_alquiler(inicio, fin)

    def test_ca1_tiempo_exactamente_un_dia_es_valido(self):
        """Si el periodo es exactamente de 24 horas, es válido y no lanza error."""
        inicio = datetime(2025, 1, 1, 10, 0, 0)
        fin = inicio + timedelta(days=1)

        # No debe lanzar excepción
        resultado = calcular_tiempo_alquiler(inicio, fin)
        assert resultado is not None


class TestCA2_DuracionTotalExacta:
    """
    Validaciones sobre el cálculo de la duración exacta en días y horas.
    """

    def test_ca2_calcula_dias_y_horas_correctamente(self):
        """Calcula una duración con días y horas extra correctamente."""
        inicio = datetime(2025, 1, 1, 10, 0, 0)
        # 2 días y 5 horas después
        fin = inicio + timedelta(days=2, hours=5)

        resultado = calcular_tiempo_alquiler(inicio, fin)

        assert resultado["dias"] == 2
        assert resultado["horas"] == 5

    def test_ca2_calcula_solo_dias_sin_horas_adicionales(self):
        """Calcula una duración exacta en días (0 horas adicionales)."""
        inicio = datetime(2025, 1, 1, 10, 0, 0)
        fin = inicio + timedelta(days=3)

        resultado = calcular_tiempo_alquiler(inicio, fin)

        assert resultado["dias"] == 3
        assert resultado["horas"] == 0

    def test_ca2_calcula_horas_adicionales_como_fraccion_de_dia(self):
        """Si sobran minutos, las horas deben contemplarlo o redondearse según la regla (asumimos truncamiento/horas completas)."""
        inicio = datetime(2025, 1, 1, 10, 0, 0)
        fin = inicio + timedelta(days=1, hours=2, minutes=30)

        resultado = calcular_tiempo_alquiler(inicio, fin)

        assert resultado["dias"] == 1
        assert resultado["horas"] == 2  # Asumiendo horas completas o truncadas

    def test_fechas_invertidas_lanza_error(self):
        """Validación extra de coherencia: fecha inicio posterior a fecha fin."""
        inicio = datetime(2025, 1, 2, 10, 0, 0)
        fin = datetime(2025, 1, 1, 10, 0, 0)

        with pytest.raises(ValueError, match="La fecha de fin debe ser posterior a la fecha de inicio"):
            calcular_tiempo_alquiler(inicio, fin)
