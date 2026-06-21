# US 9R: Incidencias de autos

**Sprint:** 7
**Actor:** Recepcionista
**Prioridad:** Media

## Descripción
**Como** recepcionista,
**quiero** ver las incidencias que reporten los conductores,
**para** tener un registro de los problemas de los autos.

## Criterios de Aceptación

### CA 1
**Dado** que un alquiler está activo,  
**cuando** el conductor genera un reporte de incidente,  
**entonces** me llega una notificación de nuevo incidente ocurrido.

### CA 2
**Dado** que quiero ver el detalle del incidente,
**cuando** clickeo la notificación,
**entonces** puedo ver la ficha técnica del incidente reportado.

### CA 3
**Dado** que han ocurrido incidentes,
**cuando** le doy al apartado de "Incidentes",
**entonces** puedo visualizar todos los incidentes ocurridos.

### CA 4
**Dado** que estoy en el historial de incidentes,
**cuando** filtro por fecha, patente o nombre de conductor,
**entonces** me aparecen sólo los resultados correspondientes al filtrado.

### CA 5
**Dado** que estoy en el historial de incidentes,
**cuando** filtro por fecha, patente o nombre de conductor que no hay registro,
**entonces** me aparecen un mensaje de "No hay incidentes correspondientes".

### CA 6
**Dado** que no han ocurrido incidentes,
**cuando** le doy al apartado de ¨Incidentes¨,
**entonces** me aparece un mensaje de "No hay incidentes registrados".		