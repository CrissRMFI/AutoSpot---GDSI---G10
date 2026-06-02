# US 3C: Configuracion del tiempo de alquiler

**Sprint:** 3  
**Actor:** Conductor  
**Prioridad:** Alta  

## Descripcion
Como conductor,  
quiero definir tiempo de alquiler,  
para verificar la disponibilidad del auto.

## Criterios de Aceptacion

### CA 1
**Dado que** el negocio establece un tiempo minimo de uso (1 dia),  
**cuando** el periodo definido entre el inicio y el fin es inferior a dicho umbral,  
**entonces** el sistema debe rechazar la solicitud.

### CA 2
**Dado que** se ha definido un periodo valido y coherente,  
**cuando** el sistema procesa la solicitud,  
**entonces** debe determinar la duracion total exacta, en horas y dias.