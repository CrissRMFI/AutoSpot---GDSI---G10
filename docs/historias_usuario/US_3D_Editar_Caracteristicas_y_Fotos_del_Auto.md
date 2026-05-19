# US 3D: Editar características y fotos del auto

**Sprint:** 2
**Actor:** Propietario
**Prioridad:** Media
**Estimación:** 3

## Descripción
**Como** dueño de un auto registrado en la plataforma,
**quiero** modificar la información técnica y las imágenes de mi perfil de auto,
**para** asegurar que la publicación refleje fielmente el estado actual del auto y sea atractiva para los inquilinos.

## Criterios de Aceptación

### CA 1
**Dado que** accedo a la sección de edición de mi auto, 
**cuando** modifico campos de características, fotos o descripción general 
**entonces** el sistema debe actualizar la ficha técnica del auto en el catálogo de forma inmediata.

### CA 2
**Dado que** estoy modificando campos obligatorios, 
**cuando** intento guardar sin completar campos obligatorios (tipo de transmisión, capacidad, marca, modelo, categoria, tipo de combustible, año del auto, pets friendly), 
**entonces** el sistema muestra un error específico y bloquea el guardado.

### CA 3
**Dado que** existen datos legales inalterables (Patente/Placa), 
**cuando** el dueño intenta editar estos campos específicos, 
**entonces** el sistema debe bloquear la edición y mostrar un mensaje indicando que para cambios de identidad debe contactar al administrador.
