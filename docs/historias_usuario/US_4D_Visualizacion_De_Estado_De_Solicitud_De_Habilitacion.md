# US 4D: Visualización de estado de solicitud de habilitación

**Sprint:** 1  
**Actor:** Propietario  
**Prioridad:** Media  

## Descripcion
***Como** duenio de un auto registrado,  
**quiero** conocer en tiempo real el estado de la revision de mis documentos y del auto,  
**para** saber si ya puedo empezar a alquilarlo o si debo corregir algun error en la carga de datos.

## Criterios de Aceptacion

### CA 1
**Dado que** envie mi solicitud de habilitacion,  
**cuando** consulto mi panel de control,  
**entonces** el sistema muestra claramente una de las etiquetas: "En Revision", "Aprobado" o "Rechazado".

### CA 2
**Dado que** mi solicitud fue "Rechazada",  
**cuando** accedo al detalle,  
**entonces** visualizo el motivo del administrador y un boton para re-subir la documentacion.

### CA 3
**Dado que** mi estado es "En Revision" o "Rechazado",  
**cuando** intento acceder a "Habilitar auto" o "Definir disponibilidad",  
**entonces** esas opciones permanecen inactivas.