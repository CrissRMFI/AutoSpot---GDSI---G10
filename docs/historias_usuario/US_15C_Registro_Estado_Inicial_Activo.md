# US 15C: Registro del estado inicial del activo (Check-in)

**Sprint:** 4
**Actor:** Conductor
**Prioridad:** Media

## Descripción
**Como** conductor,
**quiero** registrar formalmente el estado físico y operativo del auto al momento del retiro,
**para** delimitar mi responsabilidad legal sobre el activo y evitar cargos por daños preexistentes.

## Criterios de Aceptación

### CA 1
**Dado que** la identidad del conductor y el código de reserva han sido validados en la estación,
**cuando** el sistema inicia el proceso de entrega física,
**entonces** debe exigir la completitud del registro de estado inicial como requisito bloqueante antes de habilitar el uso del auto.

### CA 2
**Dado que** se realiza la inspección del activo,
**cuando** el conductor identifica anomalías estéticas o funcionales,
**entonces** el sistema debe permitir la vinculación de registros multimedia y descriptivos que actúen como prueba de preexistencia del daño.

### CA 3
**Dado que** el auto ha sido retirado de la estación y el viaje ha comenzado,
**cuando** se intenta modificar el registro de estado inicial,
**entonces** el sistema debe denegar cualquier edición.

### CA 4
**Dado que** no he terminado de realizar el check-in,
**cuando** intento salir de la estación,
**entonces** no puedo porque necesito completar el formulario.
