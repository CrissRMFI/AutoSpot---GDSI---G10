# US 10R: Historial de autos

**Sprint:** 7
**Actor:** Recepcionista
**Prioridad:** Baja

## Descripción
**Como** recepcionista,
**quiero** consultar el historial de autos que entraron y salieron,
**para** tener trazabilidad de los movimientos de la estación.

## Criterios de Aceptación

### CA 1
**Dado que** accedo al historial de autos cuando hay registros,
**entonces** veo la lista de autos con fecha, hora de entrada y salida.

### CA 2
**Dado que** veo el historial,
**cuando** filtro por estación,
**entonces** solo veo los movimientos de autos en la estación.

### CA 3
**Dado que** veo el historial,
**cuando** filtro por fecha,
**entonces** solo veo los movimientos de esa fecha.

### CA 4
**Dado que** veo el historial,
**cuando** filtro por patente,
**entonces** solo veo los movimientos de esa patente.

### CA 5
**Dado que** aplico un filtro cuando no hay registros que coincidan,
**entonces** el sistema informa que no hay resultados para ese criterio.
