# US 3C: Configuración del tiempo de alquiler

**Sprint:** 3
**Actor:** Conductor
**Prioridad:** Alta

## Descripción
**Como** conductor,
**quiero** definir tiempo de alquiler,
**para** verificar la disponibilidad del auto.

## Criterios de Aceptación

### CA 1
**Dado que** el negocio establece un tiempo mínimo de uso (1 día),
**cuando** el período definido entre el inicio y el fin es inferior a dicho umbral,
**entonces** el sistema debe rechazar la solicitud.

### CA 2
**Dado que** se ha definido un período válido y coherente,
**cuando** el sistema procesa la solicitud,
**entonces** debe determinar la duración total exacta, en horas y días.
