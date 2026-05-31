# US 7D: Actualización de precio del auto

**Sprint:** 2
**Actor:** Propietario
**Prioridad:** Media

## Descripción
**Como** dueño de un auto habilitado,
**quiero** modificar el valor del alquiler por día de mi auto,
**para** ajustar mis ganancias según la demanda del mercado o mis expectativas económicas.

## Criterios de Aceptación

### CA 1
**Dado que** actualizo el precio hoy,
**cuando** el sistema procesa el cambio,
**entonces** el nuevo valor solo se aplica a alquileres futuros, manteniendo el precio viejo para los ya pagados.

### CA 2
**Dado que** ingreso un valor extremadamente alto o bajo para la categoría,
**cuando** intento guardar,
**entonces** el sistema bloquea la acción por seguridad.

### CA 3
**Dado que** realicé una modificación,
**cuando** hago clic en guardar,
**entonces** visualizo un mensaje de confirmación antes de que el cambio sea definitivo.
