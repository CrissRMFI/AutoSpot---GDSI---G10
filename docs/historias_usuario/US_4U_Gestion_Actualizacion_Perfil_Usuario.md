# US 4U: Gestion y actualizacion de perfil de usuario

**Sprint:** 1
**Actor:** Usuario
**Prioridad:** Media

## Descripcion
**Como** usuario de la plataforma,
**quiero** modificar mi informacion personal y de contacto,
**para** asegurar que mi identidad y mis medios de comunicacion esten siempre actualizados ante el servicio.

## Criterios de Aceptacion

### CA 1
**Dado que** un usuario requiere actualizar sus datos de perfil, 
**cuando** suministra nuevos valores para atributos no criticos (ej: telefono o domicilio), 
**entonces** el sistema debe registrar estos cambios de forma permanente.

### CA 2
**Dado que** el proceso de edicion incluye la actualizacion de credenciales de acceso, 
**cuando** la nueva propuesta de seguridad no satisface los requisitos minimos de complejidad establecidos por la politica del negocio, 
**entonces** el sistema debe rechazar la actualizacion.

### CA 3
**Dado que** se solicita el cambio de un identificador de contacto principal (ej: direccion de correo electronico), 
**cuando** el identificador propuesto ya se encuentra vinculado a otra identidad activa en el sistema, 
**entonces** el sistema debe denegar la modificacion.
