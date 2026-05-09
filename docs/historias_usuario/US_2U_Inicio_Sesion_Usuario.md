# US 2U: Inicio de sesion del usuario

**Sprint:** 1
**Actor:** Usuario
**Prioridad:** Alta

## Descripcion
**Como** usuario de la plataforma,
**quiero** validar mi identidad mediante mis credenciales,
**para** acceder a las funcionalidades y datos vinculados a mi rol.

## Criterios de Aceptacion

### CA 1
**Dado que** un usuario posee una cuenta registrada, 
**cuando** proporciona sus credenciales de acceso, 
**entonces** el sistema debe verificar la autenticidad de los datos y otorgar acceso al entorno operativo correspondiente a su perfil.

### CA 2
**Dado que** se ingresan credenciales erroneas,
**cuando** el sistema procesa el intento de acceso,
**entonces** debe denegar la entrada mediante un mensaje que no revele informacion sobre la existencia de la cuenta o la validez de los campos individuales.