# US 7R: Recepción

**Sprint:** 4
**Actor:** Recepcionista
**Prioridad:** Alta

## Descripción
**Como** recepcionista,
**quiero** registrar la entrada del auto,
**para** dejar constancia de que el auto fue devuelto por el conductor.

## Criterios de Aceptación

### CA 1
**Dado que** el conductor devuelve el auto,
**cuando** registro la entrada,
**entonces** el sistema marca el alquiler como en proceso de cierre y registra la hora y fecha de entrega.

### CA 2
**Dado que** el auto fue devuelto tarde,
**cuando** registro la entrada,
**entonces** el sistema detecta el retraso y aplica automáticamente la penalización correspondiente.

### CA 3
**Dado que** intento registrar la entrada cuando no existe un alquiler activo para ese auto,
**entonces** el sistema informa que no hay alquiler en curso para ese auto.
