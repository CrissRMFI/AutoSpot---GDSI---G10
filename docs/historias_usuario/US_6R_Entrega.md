# US 6R: Entrega

**Sprint:** 4
**Actor:** Recepcionista
**Prioridad:** Alta

## Descripción
**Como** recepcionista,
**quiero** registrar la salida de un auto,
**para** dejar constancia de que el auto fue entregado al conductor.

## Criterios de Aceptación

### CA 1
**Dado que** el código fue verificado y es válido,
**cuando** registro la salida,
**entonces** el sistema me muestra un error porque el conductor aún no ha enviado el formulario de check-in.

### CA 2
**Dado que** registré la salida,
**cuando** confirmo la entrega,
**entonces** el sistema notifica al dueño.

### CA 3
**Dado que** intento registrar la salida,
**cuando** el código no fue verificado previamente,
**entonces** el sistema no permite la acción e informa que falta verificar el código de reserva.

### CA 4
**Dado que** el conductor ya terminó de realizar el check-in,
**cuando** registro la salida,
**entonces** el sistema marca el alquiler como iniciado y registra hora y fecha de salida.

### CA 5
**Dado que** el conductor ya terminó de realizar el check-in y no lo valido,
**cuando** registro la salida,
**entonces** el sistema me muestra un error porque el conductor tiene que reenviar el formulario de check-in.

### CA 6
**Dado que** no estoy de acuerdo con los datos del check-in del conductor,
**cuando** rechazo el check-in,
**entonces** el sistema me pide que especifique los motivos del rechazo.
