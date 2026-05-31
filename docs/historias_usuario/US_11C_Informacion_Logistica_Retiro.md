# US 11C: Suministro de información logística de retiro

**Sprint:** 4
**Actor:** Conductor
**Prioridad:** Alta

## Descripción
**Como** conductor,
**quiero** acceder a los detalles técnicos y geográficos de la estación de entrega,
**para** coordinar la logística de retiro físico de la unidad.

## Criterios de Aceptación

### CA 1
**Dado que** una contratación no ha alcanzado el estado de formalización requerido,
**cuando** se intenta acceder a la información específica del punto de retiro,
**entonces** el sistema debe denegar el acceso a los detalles logísticos.

### CA 2
**Dado que** el vínculo contractual se encuentra en estado habilitado para la ejecución física,
**cuando** el sistema valida la autorización de acceso a los datos de entrega,
**entonces** debe suministrar de forma automática la ubicación exacta de la unidad y franjas horarias de atención de la estación.
