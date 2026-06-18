# US 17D: Metricas de reputacion y satisfaccion

**Sprint:** 6
**Actor:** Propietario
**Prioridad:** Baja

**Descripcion:**
**Como** dueño de auto registrados y habilitados,
**quiero** visualizar un resumen de las valoraciones y comentarios de los inquilinos,
**para** identificar oportunidades de mejora en mi servicio y mantener una alta competitividad en la plataforma.

**Criterios de Aceptacion:**

1. **Dado que** accedo al dashboard de uno de mis autos, **cuando** el sistema carga los datos de reputacion, **entonces** debe mostrar un apartado visual con el promedio de estrellas y, junto a este, un enlace para acceder a las reseñas completas (replicando la estructura de la ficha tecnica del catálogo).
2. **Dado que** me encuentro viendo el resumen de estrellas, **cuando** hago clic en el enlace de reseñas, **entonces** el sistema debe desplegar la lista detallada donde pueda leer el comentario de texto, la puntuación y ver la fecha de cada testimonio histórico.
3. **Dado que** un auto recibio una calificacion menor a 3 estrellas, **cuando** visualizo el detalle de las reseñas, **entonces** el sistema debe resaltar estas valoraciones especificas con un color de advertencia para permitir una lectura prioritaria.