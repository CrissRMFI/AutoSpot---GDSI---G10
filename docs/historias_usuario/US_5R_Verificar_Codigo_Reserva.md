# US 5R: Verificar código de reserva

**Sprint:** 4
**Actor:** Recepcionista
**Prioridad:** Alta

## Descripción
**Como** recepcionista,
**quiero** verificar en el sistema el código de reserva que me presenta el conductor,
**para** confirmar que la reserva es válida y que le estoy entregando el auto a la persona correcta.

## Criterios de Aceptación

### CA 1
**Dado que** el conductor se presenta en la estación para retirar su auto,
**cuando** el recepcionista ingresa el código proporcionado por el conductor en el buscador del sistema,
**entonces** el sistema debe mostrar en pantalla la información completa de la reserva: nombre y DNI del conductor, marca/modelo/patente del auto asignado, fechas y horarios.

### CA 2
**Dado que** el recepcionista ingresa un código que existe en el sistema,
**cuando** la reserva asociada a ese código se encuentra en estado "Cancelada", "Finalizada" o la fecha de inicio ya expiró,
**entonces** el sistema debe mostrar el detalle de la reserva pero bloquear cualquier botón de "Entregar auto".

### Comportamiento operativo agregado
Cuando se genera una reserva, el sistema debe crear una notificación persistente para los usuarios administradores/recepcionistas. Al hacer clic en la notificación, debe abrirse la pantalla dedicada de verificación de código con la reserva precargada. La notificación debe mantenerse visible hasta que el código de reserva sea verificado correctamente.
