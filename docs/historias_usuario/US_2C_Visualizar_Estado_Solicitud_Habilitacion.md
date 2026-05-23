# US 2C: Visualizar estado solicitud de habilitacion

**Sprint:** 3
**Actor:** Conductor
**Prioridad:** Media

## Descripcion
**Como** conductor,
**quiero** conocer en tiempo real el estado de la revisión de mi licencia de conducir,
**para** saber si ya puedo empezar a utilizar la plataforma o si debo corregir algún error en la carga de datos.

## Criterios de Aceptacion

### CA 1
**Dado que** envié mi solicitud de habilitación, 
**cuando** consulto mi panel de control, 
**entonces** el sistema muestra claramente una de las etiquetas: "En Revisión", "Aprobado" o "Rechazado".

### CA 2
**Dado que** mi solicitud fue "Rechazada", 
**cuando** accedo al detalle, 
**entonces** visualizo el motivo del administrador y un botón para re-subir la documentación.

### CA 3
**Dado que** mi estado es "En Revisión" o "Rechazado", 
**cuando** intento alquilar un auto, 
**entonces** esas opciones permanecen inactivas.