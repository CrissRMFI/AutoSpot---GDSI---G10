# US 9D: Habilitar/Deshabilitar Auto en el momento

**Sprint:** 2
**Actor:** Propietario
**Prioridad:** Media

## Descripción
**Como** dueño de un auto habilitado,
**quiero** definir si mi auto está disponible para alquilar,
**para** tener control total sobre cuándo mi activo está generando ingresos y cuándo prefiero retirarlo de la oferta pública.

## Criterios de Aceptación

### CA 1
**Dado** que mi auto está registrado y habilitado,  
**cuando** cambio el estado a "Disponible",  
**entonces** mi auto pasa al estado disponible para alquiler y se mostrará en el catálogo de autos.

### CA 2
**Dado** que mi auto está registrado y habilitado,  
**cuando** cambio el estado a "No Disponible",  
**entonces** mi auto pasa al estado no disponible para alquiler y se dejará de mostrar en el catálogo de autos.

### CA 3
**Dado** que mi auto está registrado pero pendiente de habilitación,  
**cuando** intento cambiar el estado de disponibilidad,  
**entonces** el sistema informa que mi auto aún no fue habilitado.

### CA 4
**Dado** que el auto tiene un alquiler confirmado para este momento,  
**cuando** intento cambiar el estado a "No Disponible",  
**entonces** el sistema muestra un error:"No es posible deshabilitar el auto mientras haya una reserva o alquiler en curso".