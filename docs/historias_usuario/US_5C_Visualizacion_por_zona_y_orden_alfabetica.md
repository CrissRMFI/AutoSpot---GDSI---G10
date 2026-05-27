# US 5C: Visualización por zona y orden alfabética para la selección de estación

**Estimación:** 3
**Prioridad:** Media

## Descripción
**Como** conductor,
**quiero** identificar las estaciones por zona y ordenadas alfabéticamente,
**para** seleccionar la estación en la que quiero ver ofertas.

## Criterios de Aceptación

### CA 1
**Dado que** un conductor requiere localizar un punto de servicio,
**cuando** el sistema procesa la solicitud de exploración,
**entonces** debe incluir únicamente aquellas estaciones que estén activas, excluyendo puntos inhabilitados o por mantenimiento.

### CA 2
**Dado que** un conductor requiere localizar un punto de servicio,
**cuando** el sistema procesa la solicitud de exploración,
**entonces** debe incluir las estaciones en lista de texto, por zona y ordenadas alfabéticamente.

### CA 3
**Dado que** se selecciona un punto de retiro específico,
**cuando** se accede a la información de la estación,
**entonces** el sistema debe suministrar la dirección y las instrucciones de acceso necesarias para la operatividad del retiro, además de dar la opción de ver el catálogo.
