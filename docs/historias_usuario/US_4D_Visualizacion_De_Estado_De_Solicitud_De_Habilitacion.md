# US 4D: Visualización de estado de solicitud de habilitación

**Sprint:** 2
**Actor:** Propietario
**Prioridad:** Media

## Descripción
**Como** dueño de un auto registrado,
**quiero** conocer en tiempo real el estado de la revisión de mis documentos y del auto,
**para** saber si ya puedo empezar a alquilarlo o si debo corregir algún error en la carga de datos.

## Criterios de Aceptación

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
**cuando** intento acceder a "Habilitar auto" o "Definir disponibilidad",
**entonces** esas opciones permanecen inactivas.
