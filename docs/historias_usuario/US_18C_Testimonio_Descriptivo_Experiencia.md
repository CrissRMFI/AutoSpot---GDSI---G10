# US 18C: Testimonio descriptivo de la experiencia

**Sprint:** 5
**Actor:** Conductor
**Prioridad:** Baja

## Descripción
**Como** conductor,
**quiero** registrar un testimonio detallado sobre el alquiler finalizado,
**para** proveer información cualitativa a otros miembros de la comunidad.

## Criterios de Aceptación

### CA 1
**Dado que** una contratación ha sido cerrada administrativamente,
**cuando** el usuario suministra una descripción de su experiencia,
**entonces** el sistema debe vincular dicho relato de forma permanente al identificador del viaje y del vehículo.

### CA 2
**Dado que** se ha registrado un testimonio descriptivo,
**cuando** el sistema actualiza el registro público del activo,
**entonces** la información debe integrarse al histórico de confianza, permitiendo que sea consultada por futuros conductores para la toma de decisiones.

### CA 3
**Dado que** el sistema ya posee un testimonio registrado para una operación específica,
**cuando** se detecta un intento de duplicar o modificar el relato original,
**entonces** debe denegar la operación para garantizar la inmutabilidad y transparencia de las reseñas de la comunidad.
