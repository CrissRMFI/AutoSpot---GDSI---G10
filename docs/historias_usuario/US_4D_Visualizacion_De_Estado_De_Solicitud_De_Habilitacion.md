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

### CA 4
**Dado que** el administrador aprobó o rechazó la solicitud de habilitación de mi auto,
**cuando** ingreso a la plataforma como propietario,
**entonces** veo una notificación indicando si el auto fue habilitado o rechazado.

### CA 5
**Dado que** ya abrí la notificación de resolución de mi auto,
**cuando** vuelvo a consultar mis notificaciones,
**entonces** esa notificación no vuelve a aparecer.

### CA 6
**Dado que** tengo un auto registrado con documentación pendiente,
**cuando** ingreso a la plataforma como propietario,
**entonces** veo una notificación persistente por cada auto que todavía requiere carga de documentación.

### CA 7
**Dado que** veo una notificación persistente de documentación pendiente,
**cuando** abro la campana de notificaciones,
**entonces** la notificación permanece visible hasta que cargue la documentación del auto.

### CA 8
**Dado que** cargué la documentación requerida de un auto,
**cuando** vuelvo a consultar mis notificaciones,
**entonces** la notificación de documentación pendiente de ese auto deja de aparecer.
