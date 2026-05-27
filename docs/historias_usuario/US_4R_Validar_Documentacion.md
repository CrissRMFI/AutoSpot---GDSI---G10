# US 4R: Validar Documentacion

**Sprint:** 3 
**Actor:** Recepcionista / Admin  
**Prioridad:** Media

## Descripción

**Como** recepcionista/admin,  
**quiero** validar la documentación del conductor  y propietario,  
**para** habilitar o rechazar su registro en la plataforma.
		
## Criterios de aceptación

### CA 1
**Dado que** se ha seleccionado un documento,  
**cuando** el sistema procesa la apertura del mismo,  
**entonces** debe suministar el accedo a los archivos multimedia de identidad(DNI, licencia, etc) vinculados al perfil solicitante.

### CA 2
**Dado que** se ha completado la revisión de la documentación,  
**cuando** el recepcionista registra una resolución definitiva (Aprobación o Rechazo),  
**entonces** el sistema debe actualizar la habilitación del usuario.

### CA 3
**Dado que** una solicitud de validación ha recibido una resolución (Aprobación o Rechazo),  
**cuando** el sistema actualiza el listado de tareas pendientes,  
**entonces** debe excluir automáticamente dicho registro de la cola de espera.

### CA 4
**Dado que** el recepcionista/admin aprueba o rechaza la documentación de un vehículo,
**cuando** el sistema registra la resolución definitiva,
**entonces** debe generar una notificación para el propietario indicando si su vehículo fue habilitado o rechazado.

### CA 5
**Dado que** el propietario tiene una notificación de resolución pendiente,
**cuando** abre la notificación,
**entonces** el sistema debe marcarla como vista y no volver a mostrarla en la campana de notificaciones.
