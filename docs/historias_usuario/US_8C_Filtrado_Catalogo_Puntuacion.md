# US 8C: Motor de filtrado de catálogo por puntuación

**Sprint:** 5
**Actor:** Conductor
**Prioridad:** Media

## Descripción
**Como** conductor,
**quiero** poder filtrar la oferta de autos según su puntuación,
**para** reducir los resultados a aquellas unidades que tienen una buena puntuación.

## Criterios de Aceptación

### CA 1
**Dado que** el conductor se encuentra en el catálogo de autos,
**cuando** selecciona una puntuación específica,
**entonces** el sistema debe mostrar únicamente los autos que cumplan con esa puntuación o sea mayor a la misma.

### CA 2
**Dado que** ya se encuentra aplicado un filtro inicial,
**cuando** el usuario añade un filtro por puntuación,
**entonces** el sistema debe realizar una intersección de todas las condiciones, mostrando únicamente los autos que cumplan con la totalidad de los requisitos.

### CA 3
**Dado que** se aplican filtros por puntuación,
**cuando** la combinación de criterios solicitada no coincide con ninguna unidad disponible,
**entonces** el sistema debe informar sobre la inexistencia de coincidencias.

### CA 4
**Dado que** el catálogo se encuentra en un estado filtrado,
**cuando** se solicita eliminar los criterios de filtrado,
**entonces** el sistema debe retornar a la presentación del catálogo completo, respetando únicamente las restricciones de tiempo y ubicación definidas previamente.
