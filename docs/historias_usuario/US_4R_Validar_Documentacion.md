# US 4R: Notificación y Validar documentación

**Sprint:** 3
**Actor:** Recepcionista
**Prioridad:** Alta

## Descripción
**Como** recepcionista,
**quiero** validar la documentación del conductor y propietario,
**para** habilitar o rechazar su registro en la plataforma.

## Criterios de Aceptación

### CA 1
**Dado que** se ha seleccionado un documento,
**cuando** el sistema procesa la apertura del mismo,
**entonces** debe suministrar el acceso a los archivos multimedia de identidad (DNI, licencia, etc.) vinculados al perfil solicitante.

### CA 2
**Dado que** se ha completado la revisión de la documentación,
**cuando** el recepcionista registra una resolución definitiva (Aprobación o Rechazo),
**entonces** el sistema debe actualizar la habilitación del usuario.

### CA 3
**Dado que** una solicitud de validación ha recibido una resolución (Aprobación o Rechazo),
**cuando** el sistema actualiza el listado de tareas pendientes,
**entonces** debe excluir automáticamente dicho registro de la cola de espera.
