# US 1C: Cargar de identidad y documentación habilitante

**Sprint:** 2
**Actor:** Conductor
**Prioridad:** Alta

## Descripción
**Como** conductor,
**quiero** proporcionar licencia de conducir,
**para** que el sistema valide mi identidad y mi aptitud legal para operar los autos de la plataforma.

## Criterios de Aceptación

### CA 1
**Dado que** el usuario se encuentra en la sección de "Validación de Identidad",
**cuando** proporciona imagen de la licencia de conducir,
**entonces** el sistema debe permitir la subida.

### CA 2
**Dado que** el usuario intenta cargar un documento cuando el archivo no cumple con el formato permitido o excede el peso máximo,
**entonces** el sistema debe mostrar un mensaje de error específico.

### CA 3
**Dado que** el usuario completó la carga de la licencia,
**cuando** envía la información,
**entonces** el estado de su cuenta debe cambiar a "Pendiente de Validación" y el sistema debe bloquear el acceso al flujo de reserva de autos.

### CA 4
**Dado que** el usuario tiene el documento en estado "Pendiente de Validación",
**cuando** se aprueba la documentación,
**entonces** el usuario debe recibir una notificación email y su estado debe cambiar a "Habilitado".

### CA 5
**Dado que** se detecta una anomalía en la información,
**cuando** el documento es rechazado indicando el motivo,
**entonces** el sistema debe notificar al usuario y devolverle toda la información para permitir una nueva carga.

### CA 6
**Dado que** el usuario ingresa su licencia cuando corresponde con la categoría de licencia principiante,
**entonces** el sistema rechaza el registro e informa que no se aceptan conductores en categoría principiante.
