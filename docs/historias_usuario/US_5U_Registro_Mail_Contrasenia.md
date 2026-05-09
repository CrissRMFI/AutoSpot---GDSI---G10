# US 5U: Registrarse con mail y contrasenia

**Sprint:** 1
**Actor:** Usuario
**Prioridad:** Media

## Descripcion
**Como** nuevo usuario 
**quiero** registrarme con mail y contrasenia
**para** crear una cuenta en la plataforma

## Criterios de Aceptacion

### CA 1
**Dado que** un nuevo usuario intenta registrarse, 
**cuando** ingresa en el campo de mail algo que no lo es, 
**entonces** el sistema tira un error de "Mail invalido".

### CA 2
**Dado que** un nuevo usuario intenta registrarse, 
**cuando** ingresa una contrasenia de menos de 8 caracteres, 
**entonces** el sistema tira un error de "La contrasenia debe tener minimo 8 caracteres".

### CA 3
**Dado que** un nuevo usuario intenta registrarse, 
**cuando** quiere darle al boton de registrarse sin completar los campos de mail y contrasenia, 
**entonces** no puede porque el boton esta deshabilitado.

### CA 4
**Dado que** un nuevo usuario intenta registrarse, 
**cuando** quiere darle al boton de registrarse despues de completar correctamente ambos campos, 
**entonces** se registra exitosamente.

### CA 5
**Dado que** un nuevo usuario intenta registrarse, 
**cuando** quiere registrar un mail ya existente en la plataforma, 
**entonces** el sistema tira un error de "Mail existente".
