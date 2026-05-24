# US 3R: Abrir documentación

**Sprint:** 4  
**Actor:** Recepcionista / Admin  
**Prioridad:** Media

## Descripción

**Como** recepcionista/admin,  
**quiero** abrir una solicitud de documentación desde la cola de revisión,  
**para** ver los datos y archivos enviados antes de validar la documentación.

## Criterios de aceptación

### CA 1
**Dado que** existen solicitudes de documentación en la cola,  
**cuando** selecciono una solicitud,  
**entonces** el sistema navega a una página dedicada de detalle.

### CA 2
**Dado que** la solicitud corresponde a un vehículo,  
**cuando** abro su documentación,  
**entonces** veo sus datos legales, estado, usuario asociado y documentos adjuntos.

### CA 3
**Dado que** la solicitud corresponde a un conductor,  
**cuando** abro su documentación,  
**entonces** veo los datos de licencia, estado, usuario asociado y fotos de frente/dorso.

### CA 4
**Dado que** estoy viendo documentos con imagen,  
**cuando** hago click sobre una vista previa,  
**entonces** la imagen se abre ampliada en un modal.

### CA 5
**Dado que** no tengo rol ADMIN,  
**cuando** intento abrir una solicitud,  
**entonces** el sistema rechaza la operación.

## Implementación

- Backend:
  - `GET /admin/solicitudes-documentacion/{tipo}/{recurso_id}`
  - Tipos soportados: `VEHICULO`, `CONDUCTOR`.
  - Requiere JWT y rol `ADMIN`.
- Frontend:
  - Página dedicada:
    - `/admin/solicitudes-documentacion/:tipo/:recursoId`
  - Vista responsive desktop/mobile.
  - Previews de imágenes y modal de ampliación.
- Base de datos:
  - No requiere migración; lee datos ya existentes.
- Tests:
  - Servicio + HTTP + seguridad.
