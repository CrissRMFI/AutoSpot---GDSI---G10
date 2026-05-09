# US 3U: Finalizacion de sesion del usuario

**Sprint:** 1
**Actor:** Usuario
**Prioridad:** Alta

## Descripcion
**Como** usuario con una sesion activa,
**quiero** terminar mi acceso al sistema,
**para** asegurar la privacidad de mi informacion y evitar el uso no autorizado de mi cuenta.

## Criterios de Aceptacion

### CA 1
**Dado que** un usuario esta activo en plataforma, 
**cuando** solicita la finalizacion de su sesion, 
**entonces** el sistema debe invalidar los permisos de acceso actuales de forma inmediata, requiriendo una nueva autenticacion para cualquier operacion posterior.

### CA 2
**Dado que** existe una sesion iniciada sin actividad detectada, 
**cuando** el tiempo transcurrido supera el limite de seguridad establecido por el negocio, 
**entonces** el sistema debe finalizar la sesion automaticamente para proteger la integridad del entorno del usuario.
