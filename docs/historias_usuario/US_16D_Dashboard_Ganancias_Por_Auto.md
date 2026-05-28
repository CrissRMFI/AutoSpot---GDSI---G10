# US 16D: Dashboard de ganancias por auto

**Sprint:** 7
**Actor:** Propietario
**Prioridad:** Media

## Descripción
**Como** dueño de un auto específico registrado en la plataforma,
**quiero** visualizar el desglose detallado de los ingresos y métricas de uso de esa unidad,
**para** entender su rentabilidad individual y tomar decisiones sobre su mantenimiento o permanencia en el servicio.

## Criterios de Aceptación

### CA 1
**Dado que** estoy en la sección de "Mis autos" y selecciono una unidad,
**cuando** accedo al Dashboard de ganancias,
**entonces** el sistema debe mostrar la patente, marca, modelo y categoría del auto.

### CA 2
**Dado que** estoy visualizando el Dashboard,
**cuando** selecciono un rango de fechas (ej: "Esta semana"),
**entonces** el total de ingresos y días alquilados se actualiza para mostrar solo los datos de ese período.

### CA 3
**Dado que** el auto estuvo disponible 30 días y se alquiló 15,
**cuando** el sistema calcula la métrica,
**entonces** debe mostrar un indicador de "50% de Tasa de Ocupación".
