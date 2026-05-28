# US 17C: Valoración cuantitativa del servicio

**Sprint:** 5
**Actor:** Conductor
**Prioridad:** Baja

## Descripción
**Como** conductor,
**quiero** asignar un puntaje numérico a la experiencia de uso,
**para** cuantificar la calidad del servicio y afectar la métrica de reputación del activo.

## Criterios de Aceptación

### CA 1
**Dado que** se ha finalizado una contratación y se ha registrado la devolución física,
**cuando** el sistema habilita el ingreso del puntaje,
**entonces** debe permitir únicamente valores dentro de la escala establecida por el negocio (ej: 1 a 5).

### CA 2
**Dado que** el valor suministrado se encuentra fuera del rango permitido,
**cuando** se intenta procesar la valoración,
**entonces** el sistema debe invalidar el ingreso para preservar la integridad de las métricas.

### CA 3
**Dado que** se ha registrado un puntaje válido,
**cuando** el sistema consolida la información,
**entonces** debe actualizar automáticamente el promedio de reputación del vehículo y del propietario en el registro histórico.
