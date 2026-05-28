# US 19D: Recarga de documentos ya validados

**Sprint:** 4
**Actor:** Propietario
**Prioridad:** Baja

## Descripción
**Como** dueño de auto registrado y habilitado,
**quiero** cargar una nueva solicitud de nueva documentación de mi auto ya habilitado anteriormente,
**para** que la página esté actualizada.

## Criterios de Aceptación

### CA 1
**Dado que** quiero actualizar la documentación de mi auto y tengo el auto marcado como disponible,
**cuando** intento mandar una nueva solicitud de documentación,
**entonces** el sistema no debe permitirme mandar la documentación y mostrar el mensaje "El auto está marcado como disponible, debe deshabilitarlo para poder volver a mandar una solicitud de documentación".

### CA 2
**Dado que** mi auto está en un alquiler activo,
**cuando** intento mandar una nueva solicitud de documentación,
**entonces** debe mostrar "Auto en alquiler, debe esperar que termine el alquiler activo y deshabilitarlo para poder volver a mandar una solicitud de documentación".

### CA 3
**Dado que** mi auto está deshabilitado,
**cuando** intento mandar una nueva solicitud de documentación,
**entonces** se debe hacer la solicitud exitosa y espero de vuelta el proceso de validación.
