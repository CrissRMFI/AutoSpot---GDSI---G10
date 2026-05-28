# US 2R: Priorización cronológica de las solicitudes

**Sprint:** 3
**Actor:** Recepcionista
**Prioridad:** Alta

## Descripción
**Como** recepcionista,
**quiero** que la lista de las solicitudes mantenga una jerarquía temporal,
**para** asegurar la atención equitativa según el orden de ingreso de los trámites.

## Criterios de Aceptación

### CA 1
**Dado que** el sistema gestiona múltiples solicitudes en simultáneo,
**cuando** se genera la secuencia de datos para la revisión,
**entonces** debe aplicar un ordenamiento cronológico ascendente (del más antiguo al más reciente).

### CA 2
**Dado que** se incorporan nuevos registros de documentación a la plataforma,
**cuando** el sistema actualiza la lista de solicitudes,
**entonces** debe posicionar automáticamente los nuevos ingresos al final de la secuencia temporal.
