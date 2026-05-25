# US 7C: Motor de filtrado de catálogo por características

**Sprint:** 3
**Actor:** Conductor
**Prioridad:** Media

## Descripcion
**Como** conductor,
**quiero** poder filtrar la oferta de autos según criterios específicos,
**para** reducir los resultados a aquellas unidades que satisfacen mis requisitos técnicos y de preferencia.

## Criterios de Aceptacion

### CA 1
**Dado que** el conductor se encuentra en el catálogo de autos, 
**cuando** selecciona un valor de filtro específico (transmisión, capacidad, marca, categoría, tipo de combustible, antigüedad, pets friendly), 
**entonces** el sistema debe mostrar únicamente los autos que cumplan con esa condición exacta.

### CA 2
**Dado que** ya se encuentra aplicado un filtro inicial, 
**cuando** el usuario añade criterios de filtrado adicionales, 
**entonces** el sistema debe realizar una intersección de todas las condiciones, mostrando únicamente los autos que cumplan con la totalidad de los requisitos.

### CA 3
**Dado que** se aplican filtros sobre el catálogo, 
**cuando** la combinación de criterios solicitada no coincide con ninguna unidad disponible, 
**entonces** el sistema debe informar sobre la inexistencia de coincidencias.

### CA 4
**Dado que** el catálogo se encuentra en un estado filtrado, 
**cuando** se solicita eliminar los criterios de filtrado, 
**entonces** el sistema debe retornar a la presentación del catálogo completo, respetando únicamente las restricciones de tiempo y ubicación definidas previamente.
